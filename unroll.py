import cv2
import numpy as np
import math
import argparse

def crop_sector_to_rect(image_path: str, start_angle: float, end_angle: float, output_path: str):
    """
    剪切扇形区域，并将其放入一个以半径为高、以扇形高度为宽的黑色长方形画布中。

    :param image_path: 输入的正方形图片路径。
    :param start_angle: 扇形的起始角度（度数）。
    :param end_angle: 扇形的结束角度（度数）。
    :param output_path: 输出的图片路径。
    """
    # 1. 加载图片并获取基本信息
    image = cv2.imread(image_path)
    if image is None:
        print(f"错误：无法加载图片 {image_path}")
        return

    height, width, _ = image.shape
    center_x, center_y = width // 2, height // 2
    radius = width // 2

    # 2. 创建一个黑色的掩码画布 (与原图等大)
    mask = np.zeros((height, width), dtype=np.uint8)
    cv2.ellipse(
        img=mask,
        center=(center_x, center_y),
        axes=(radius, radius),
        angle=0,
        startAngle=360 - end_angle,
        endAngle=360 - start_angle,
        color=255,
        thickness=-1
    )

    # 3. 使用掩码“剪切”原始图片
    image_with_sector_only = cv2.bitwise_and(image, image, mask=mask)

    # 4. 计算新画布的尺寸
    output_height = radius  # 长边是半径
    # 宽度是扇形的垂直高度
    output_width = int(np.ceil(radius * np.sin(np.deg2rad(end_angle))))

    # 5. 创建最终的黑色长方形画布
    output_image = np.zeros((output_height, output_width, 3), dtype=np.uint8)

    # 6. 从原图中裁剪出包含扇形的相关区域
    # 这个区域的左上角是 (center_x, center_y - output_width)
    # 尺寸是 (radius, output_width)
    src_y_start = center_y - output_width
    src_y_end = center_y
    src_x_start = center_x
    src_x_end = center_x + radius
    
    cropped_region = image_with_sector_only[src_y_start:src_y_end, src_x_start:src_x_end]

    # 7. 旋转和翻转裁剪区域以适应输出画布
    # cv2.rotate(src, cv2.ROTATE_90_COUNTERCLOCKWISE)
    rotated_region = cv2.rotate(cropped_region, cv2.ROTATE_90_COUNTERCLOCKWISE)
    # cv2.flip(src, 1) -> 水平翻转
    final_region = cv2.flip(rotated_region, 1)
    
    # 8. 将处理好的区域粘贴到最终画布上
    h_final, w_final, _ = final_region.shape
    output_image[0:h_final, 0:w_final] = final_region

    # # 镜像翻转（水平翻转，flipCode=1；垂直翻转，flipCode=0）
    # output_image = cv2.flip(output_image, 1)  # 水平镜像

    # 9. 保存结果图片前，对角线翻转
    output_image = cv2.transpose(output_image)  # 主对角线翻转
    output_image = cv2.flip(output_image, 1)    # 水平翻转，得到副对角线翻转
    output_image = cv2.flip(output_image, 0)  # 水平镜像
    cv2.imwrite(output_path, output_image)
    print(f"最终长方形图片已保存到: {output_path}")

def create_visualization(image_path: str, start_angle: float, end_angle: float, output_vis_path: str):
    image = cv2.imread(image_path)
    if image is None:
        return
    
    vis_image = image.copy()
    overlay = vis_image.copy()

    height, width, _ = image.shape
    center = (width // 2, height // 2)
    radius = width // 2

    cv2.ellipse(overlay, center, (radius, radius), 0, 360 - end_angle, 360 - start_angle, (0, 255, 255), -1)
    alpha = 0.4
    vis_image = cv2.addWeighted(overlay, alpha, vis_image, 1 - alpha, 0)

    start_point = (
        int(center[0] + radius * np.cos(np.deg2rad(start_angle))),
        int(center[1] - radius * np.sin(np.deg2rad(start_angle)))
    )
    cv2.line(vis_image, center, start_point, (0, 0, 255), 2)

    end_point = (
        int(center[0] + radius * np.cos(np.deg2rad(end_angle))),
        int(center[1] - radius * np.sin(np.deg2rad(end_angle)))
    )
    cv2.line(vis_image, center, end_point, (255, 0, 0), 2)

    cv2.imwrite(output_vis_path, vis_image)

    print(f"中间可视化结果已保存到: {output_vis_path}")

# 由于图片只能够处理圆内部分，因此这里提供一个辅助函数，用于只保留图片中心圆内的内容，圆外全部变黑。
# 用了很多方法想让ai去截取对应范围的内容,但是效果都不理想,主要是需要有一个边是直线的截取方法,所以最好就是截取0到x度,或者x度到90度的内容这种方式
# 在opencv中,这种方法是基于极坐标来实现的,极坐标的0度是横着的,而不是竖着的,不是像月球经纬度的那样子描述的
#由于blender中UV的背景一定是一个正方形,所以这里直接生成的图像其实是一个正方形的,然后只保留需要截取的圆形部分,其余内容全部都是黑色的

#对极地立体投影的图像进行一个圆形掩码处理，
def mask_circle(image_path: str, output_path: str):
    """
    只保留图片中心圆内的内容，圆外全部变黑。
    圆心为图片中心，半径为图片边长的一半。

    :param image_path: 输入图片路径
    :param output_path: 输出图片路径
    """
    image = cv2.imread(image_path)
    if image is None:
        print(f"无法读取图片: {image_path}")
        return

    height, width = image.shape[:2]
    center = (width // 2, height // 2)
    radius = min(width, height) // 2

    # 创建掩码
    mask = np.zeros((height, width), dtype=np.uint8)
    cv2.circle(mask, center, radius, 255, -1)

    # 应用掩码
    result = cv2.bitwise_and(image, image, mask=mask)

    cv2.imwrite(output_path, result)
    print(f"已保存结果图片到: {output_path}")
#对极地立体投影的图像顺时针旋转一定角度
def mask_circle_and_rotate(image_path: str, output_path: str, angle: float):
    """
    只保留图片中心圆内的内容，圆外全部变黑，并顺时针旋转指定角度。
    :param image_path: 输入图片路径
    :param output_path: 输出图片路径
    :param angle: 顺时针旋转角度（度）
    """
    image = cv2.imread(image_path)
    if image is None:
        print(f"无法读取图片: {image_path}")
        return

    height, width = image.shape[:2]
    center = (width // 2, height // 2)
    radius = min(width, height) // 2

    # 创建掩码
    mask = np.zeros((height, width), dtype=np.uint8)
    cv2.circle(mask, center, radius, 255, -1)

    # 应用掩码
    result = cv2.bitwise_and(image, image, mask=mask)

    # 顺时针旋转
    rot_mat = cv2.getRotationMatrix2D(center, -angle, 1.0)
    rotated = cv2.warpAffine(result, rot_mat, (width, height), borderValue=(0,0,0))

    cv2.imwrite(output_path, rotated)
    print(f"已保存旋转后的结果图片到: {output_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="转换tif文件")
    parser.add_argument("src", type=str, help="源TIF或者png文件路径")
    parser.add_argument("--rotate", action="store_true", help="生成圆形外的遮罩，并旋转对应角度")
    args = parser.parse_args()
    # --- 参数设置 ---
    input_image_file = args.src
    output_image_file = r"C:\Users\MushOtter\Pictures\cropped_rect1.png" # 修改输出文件名
    visualization_file = r"C:\Users\MushOtter\Pictures\mid_visualization.png"

    start_deg = 70
    end_deg = 90

    # --- 检查并创建示例图片 (如果需要) ---
    try:
        with open(input_image_file):
            pass
    except FileNotFoundError:
        print(f"错误：输入文件 '{input_image_file}' 不存在。正在创建示例图片...")
        sample_img = np.zeros((400, 400, 3), dtype=np.uint8)
        cv2.circle(sample_img, (200, 200), 190, (0, 255, 0), 5)
        cv2.putText(sample_img, 'Sample Image', (80, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.imwrite(input_image_file, sample_img)

    # --- 任务执行 ---
    if(not args.rotate):
        crop_sector_to_rect(input_image_file, start_deg, end_deg, output_image_file)
        create_visualization(input_image_file, start_deg, end_deg, visualization_file)
    else:
        mask_circle_and_rotate(input_image_file, r"C:\Users\MushOtter\Pictures\rotate.tif", angle=20)