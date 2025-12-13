from PIL import Image, ImageSequence
import os

def swap_tiff_halves(input_path, output_path):
    """
    加载一个TIFF图片（可以是单页或多页），
    对每一页进行左右两半的交换，然后保存结果。
    """
    try:
        # 1. 加载图片
        img = Image.open(input_path)
        print(f"成功加载TIFF图片: {input_path}")

        processed_frames = []
        
        # 2. 迭代处理TIFF中的每一帧（或页面）
        for i, page in enumerate(ImageSequence.Iterator(img)):
            print(f"正在处理第 {i+1} 帧...")
            
            # 为了方便处理，我们通常将图像转换为 'RGB' 模式。
            # 如果您的TIFF是单通道灰度图，也可以用 'L' 模式。
            # Pillow 会处理好不同位深度（如16位）的转换。
            page = page.convert("RGB") 
            
            width, height = page.size
            print(f"  帧尺寸: {width}x{height}")

            # 3. 计算中心线并裁剪
            midpoint = width // 2
            left_box = (0, 0, midpoint, height)
            right_box = (midpoint, 0, width, height)
            left_half = page.crop(left_box)
            right_half = page.crop(right_box)

            # 4. 创建新帧并拼接
            new_frame = Image.new('RGB', (width, height))
            new_frame.paste(right_half, (0, 0))
            new_frame.paste(left_half, (midpoint, 0))
            
            processed_frames.append(new_frame)
            print(f"  第 {i+1} 帧处理完成。")

        # 5. 保存结果
        if not processed_frames:
            print("错误: 未找到可处理的帧。")
            return

        # 使用无损压缩保存，以减小文件大小
        compression_method = "tiff_deflate"

        if len(processed_frames) > 1:
            # 如果是多帧TIFF，保存所有处理过的帧
            processed_frames[0].save(
                output_path, 
                save_all=True, 
                append_images=processed_frames[1:],
                compression=compression_method
            )
            print(f"处理完成！包含 {len(processed_frames)} 帧的新TIFF图片已保存至: {output_path}")
        else:
            # 如果是单帧TIFF
            processed_frames[0].save(output_path, compression=compression_method)
            print(f"处理完成！新图片已保存至: {output_path}")

    except FileNotFoundError:
        print(f"错误: 输入文件未找到 '{input_path}'")
    except Exception as e:
        print(f"处理过程中发生错误: {e}")

if __name__ == '__main__':
    # --- 使用说明 ---
    # 1. 确保已安装 Pillow: pip install Pillow
    #    在某些系统上，处理复杂的TIFF可能需要额外的库支持，但Pillow通常足够。
    # 2. 将 'input_image.tif' 替换为您的TIFF文件路径。
    # 3. 'output_image.tif' 是处理后保存的文件名。
    
    input_file = r"D:\All_moon_128\outputFile\lroc_color_poles_8k.tif" # <-- 修改这里
    output_file = r"D:\All_moon_128\outputFile\lroc_color_poles_8k_swap.tif" # <-- 修改这里

    if not os.path.exists(input_file):
        print(f"'{input_file}' 不存在。请创建一个名为 '{input_file}' 的图片文件或修改脚本中的路径。")
    else:
        swap_tiff_halves(input_file, output_file)
