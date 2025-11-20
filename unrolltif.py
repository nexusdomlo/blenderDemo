import cv2
import numpy as np
import math
import argparse
import tifffile  # 导入 tifffile 库

def crop_sector_to_rect(image_path: str, start_angle: float, end_angle: float, output_path: str):
    """
    剪切扇形区域，并将其放入一个以半径为高、以扇形高度为宽的黑色长方形画布中。
    支持高位深 TIF 文件。
    """
    # 1. 加载图片并获取基本信息
    # 使用 tifffile 读取，以支持高位深图像
    image = tifffile.imread(image_path)
    if image is None:
        return

    # 兼容单通道和多通道
    if len(image.shape) == 2:
        height, width = image.shape
        channels = 1
        # 创建一个用于 OpenCV 操作的 8-bit BGR 版本
        image_for_cv_ops = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        image_for_cv_ops = cv2.cvtColor(image_for_cv_ops, cv2.COLOR_GRAY2BGR)
    else:
        height, width, channels = image.shape
        # 如果是多通道（如RGB/RGBA），创建一个 8-bit BGR 版本用于 OpenCV 操作
        # 我们只取前三个通道进行可视化和掩码操作
        image_for_cv_ops = cv2.normalize(image[:,:,:3], None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)

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

    # 3. 使用掩码“剪切”原始图片（在原始高位深数据上应用掩码）
    # 为了应用掩码，我们需要确保 image 和 mask 的维度兼容
    # 我们将掩码扩展到与图像通道数相同的维度
    if channels > 1:
        # 创建一个与原图同样大小和数据类型的黑色图像
        black_background = np.zeros_like(image)
        # 将掩码应用到每个通道
        image_with_sector_only = np.where(mask[..., np.newaxis] != 0, image, black_background)
    else:
        black_background = np.zeros_like(image)
        image_with_sector_only = np.where(mask != 0, image, black_background)


    # 4. 计算新画布的尺寸
    output_height = radius
    output_width = int(np.ceil(radius * np.sin(np.deg2rad(end_angle))))

    # 5. 创建最终的黑色长方形画布（保持原始数据类型和通道数）
    if channels > 1:
        output_image = np.zeros((output_height, output_width, channels), dtype=image.dtype)
    else:
        output_image = np.zeros((output_height, output_width), dtype=image.dtype)


    # 6. 从原图中裁剪出包含扇形的相关区域
    src_y_start = center_y - output_width
    src_y_end = center_y
    src_x_start = center_x
    src_x_end = center_x + radius
    
    cropped_region = image_with_sector_only[src_y_start:src_y_end, src_x_start:src_x_end]

    # 7. 旋转和翻转裁剪区域以适应输出画布
    # 注意：cv2.rotate 和 cv2.flip 支持多通道和高位深图像
    rotated_region = cv2.rotate(cropped_region, cv2.ROTATE_90_COUNTERCLOCKWISE)
    final_region = cv2.flip(rotated_region, 1)
    
    # 8. 将处理好的区域粘贴到最终画布上
    h_final, w_final = final_region.shape[:2]
    output_image[0:h_final, 0:w_final] = final_region

    # 9. 保存结果图片前，对角线翻转
    output_image = cv2.transpose(output_image)
    output_image = cv2.flip(output_image, 1)
    output_image = cv2.flip(output_image, 0)
    
    # 使用 tifffile 保存，保留数据类型
    tifffile.imwrite(output_path, output_image)
    print(f"最终长方形图片已保存到: {output_path}")

def create_visualization(image_path: str, start_angle: float, end_angle: float, output_vis_path: str):
    # 可视化函数主要用于调试，通常转为 8-bit RGB 图像进行处理
    image = tifffile.imread(image_path)
    if image is None:
        return

    # 兼容单通道和多通道，并统一转换为 8-bit BGR 用于可视化
    if len(image.shape) == 2:
        # 从高位深灰度图转为 8-bit BGR
        vis_image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        vis_image = cv2.cvtColor(vis_image, cv2.COLOR_GRAY2BGR)
    else:
        # 从高位深多通道图转为 8-bit BGR
        vis_image = cv2.normalize(image[:,:,:3], None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    
    height, width, _ = vis_image.shape
    overlay = vis_image.copy()
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

    # 可视化结果通常保存为 PNG 或 JPG，但这里我们用 tifffile 保存为 TIF
    tifffile.imwrite(output_vis_path, vis_image)
    print(f"中间可视化结果已保存到: {output_vis_path}")

def mask_circle(image_path: str, output_path: str):
    """
    只保留图片中心圆内的内容，圆外全部变黑。
    """
    image = tifffile.imread(image_path)
    if image is None:
        return

    if len(image.shape) == 2:
        height, width = image.shape
    else:
        height, width, _ = image.shape
    center = (width // 2, height // 2)
    radius = min(width, height) // 2

    mask = np.zeros((height, width), dtype=np.uint8)
    cv2.circle(mask, center, radius, 255, -1)

    # 使用 np.where 应用掩码以支持高位深
    if len(image.shape) > 2:
        black_background = np.zeros_like(image)
        result = np.where(mask[..., np.newaxis] != 0, image, black_background)
    else:
        black_background = np.zeros_like(image)
        result = np.where(mask != 0, image, black_background)

    tifffile.imwrite(output_path, result)
    print(f"已保存结果图片到: {output_path}")

def mask_circle_and_rotate(image_path: str, output_path: str, angle: float):
    """
    只保留图片中心圆内的内容，圆外全部变黑，并逆时针旋转指定角度。
    """
    image = tifffile.imread(image_path)
    if image is None:
        return

    if len(image.shape) == 2:
        height, width = image.shape
    else:
        height, width, _ = image.shape
    center = (width // 2, height // 2)
    radius = min(width, height) // 2

    mask = np.zeros((height, width), dtype=np.uint8)
    cv2.circle(mask, center, radius, 255, -1)

    if len(image.shape) > 2:
        black_background = np.zeros_like(image)
        result = np.where(mask[..., np.newaxis] != 0, image, black_background)
    else:
        black_background = np.zeros_like(image)
        result = np.where(mask != 0, image, black_background)

    rot_mat = cv2.getRotationMatrix2D(center, angle, 1.0)
    # borderValue 需要与图像数据类型匹配
    border_val = tuple([0] * image.shape[2]) if len(image.shape) > 2 else 0
    rotated = cv2.warpAffine(result, rot_mat, (width, height), borderValue=border_val)

    tifffile.imwrite(output_path, rotated)
    print(f"已保存旋转后的结果图片到: {output_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="转换tif文件")
    parser.add_argument("src", type=str, help="源TIF或者png文件路径")
    parser.add_argument("--rotate", action="store_true", help="生成圆形外的遮罩，并旋转对应角度")
    args = parser.parse_args()
    
    input_image_file = args.src
    # 处理tif和png两种格式
    if(input_image_file.lower().endswith('.tif')==False and input_image_file.lower().endswith('.tiff')==False):
        print("用png图进行转换")
        output_image_file = r"C:\Users\MushOtter\Pictures\cropped_rect.png"
        visualization_file = r"C:\Users\MushOtter\Pictures\visualization.png"
    else:
        print("用tif图进行转换")
        output_image_file = r"C:\Users\MushOtter\Pictures\cropped_rect.tif"
        visualization_file = r"C:\Users\MushOtter\Pictures\visualization.tif"

    start_deg = 70
    end_deg = 90

    if(input_image_file.lower().endswith('.tif')==False and input_image_file.lower().endswith('.tiff')==False):
        try:
            # 使用 tifffile 检查文件是否存在
            with open(input_image_file, 'rb') as f:
                tifffile.TiffFile(f)
        except (FileNotFoundError, tifffile.TiffFileError):
            print(f"错误：输入文件 '{input_image_file}' 不是有效的TIF或不存在。请检查你的文件是否存在")
    else:
        try:
            with open(input_image_file):
                pass
        except FileNotFoundError:
            print(f"错误：输入文件 '{input_image_file}' 不是有效的TIF或不存在。请检查你的文件是否存在")

    if(not args.rotate):
        crop_sector_to_rect(input_image_file, start_deg, end_deg, output_image_file)
        create_visualization(input_image_file, start_deg, end_deg, visualization_file)
    else:
        mask_circle_and_rotate(input_image_file, r"C:\Users\MushOtter\Pictures\rotate.tif", angle=20)