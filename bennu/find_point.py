import argparse
from PIL import Image, ImageDraw
import numpy as np
from astropy.io import fits
import os

def convert_fits_to_image(fits_path):
    """
    读取FITS文件，将其数据归一化，并返回一个Pillow图像对象。
    """
    print(f"正在读取FITS文件: {fits_path}")
    try:
        with fits.open(fits_path) as hdul:
            data = hdul[0].data
            if data is None:
                print("错误: FITS文件中没有找到图像数据。")
                return None

            data = np.nan_to_num(data)
            vmin = np.min(data)
            vmax = np.max(data)
            print(f"FITS数据范围: min={vmin}, max={vmax}")

            if vmax - vmin == 0:
                normalized_data = np.zeros_like(data)
            else:
                normalized_data = (data - vmin) / (vmax - vmin) * 255.0
            
            image_array = normalized_data.astype(np.uint8)
            
            # --- 修正步骤 ---
            # FITS标准原点在左下角，Pillow在左上角。垂直翻转数组以匹配。
            image_array_flipped = np.flipud(image_array)
            
            # 从翻转后的数组创建图像
            img = Image.fromarray(image_array_flipped, mode='L')
            
            print("FITS文件已成功转换为内存中的图像 (并已垂直翻转以匹配FITS标准)。")
            return img

    except FileNotFoundError:
        print(f"错误: 找不到FITS文件 '{fits_path}'")
        return None
    except Exception as e:
        print(f"读取或转换FITS文件时发生错误: {e}")
        return None


def mark_points_on_image(img, points, output_path, cross_size=10, color="red", line_width=2):
    """
    在给定的Pillow图像对象上标记坐标点。
    """
    try:
        img = img.convert("RGB")
        draw = ImageDraw.Draw(img)
        img_width, img_height = img.size
        print(f"图像尺寸: {img_width}x{img_height}")

        for point in points:
            x_cartesian, y_cartesian = point
            
            # 坐标系转换 (左下角 -> 左上角)
            x_img = x_cartesian
            y_img = img_height - y_cartesian
            
            print(f"标记点: (x={x_cartesian}, y={y_cartesian}) -> 图像坐标: (x={x_img}, y={y_img})")

            p1_start = (x_img - cross_size, y_img - cross_size)
            p1_end = (x_img + cross_size, y_img + cross_size)
            p2_start = (x_img - cross_size, y_img + cross_size)
            p2_end = (x_img + cross_size, y_img - cross_size)
            
            draw.line([p1_start, p1_end], fill=color, width=line_width)
            draw.line([p2_start, p2_end], fill=color, width=line_width)

        img.save(output_path)
        print(f"\n标记完成！已保存到: {output_path}")

    except Exception as e:
        print(f"标记图像时发生错误: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="转换FITS文件并在指定点标记")
    parser.add_argument("src", type=str, help="源FITS文件路径")
    parser.add_argument("point", type=str, help="要标记的点，格式为x,y")
    args = parser.parse_args()
    
    INPUT_IMAGE_PATH = args.src
    point_str = args.point
    try:
        x_str, y_str = point_str.split(',')
        x = int(x_str)
        y = int(y_str)
    except ValueError:
        print("错误: 'point'参数格式不正确。请使用 'x,y' 格式，例如 '779,427'")
        exit()

    dirpath, _ = os.path.split(INPUT_IMAGE_PATH)
    OUTPUT_IMAGE_PATH = os.path.join(dirpath, "marked_image.png")

    points_to_mark = [(x, y)]

    image_to_mark = convert_fits_to_image(INPUT_IMAGE_PATH)

    if image_to_mark:
        mark_points_on_image(image_to_mark, points_to_mark, OUTPUT_IMAGE_PATH)
