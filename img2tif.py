import os
import subprocess
import argparse

# 配置参数
img_dir = "D:\\Moon"      # IMG文件夹路径
tif_dir = "D:\\Moon"      # TIF输出路径
clip_dir = "D:\\Moon"    # 裁剪后TIF输出路径
os.makedirs(tif_dir, exist_ok=True)
os.makedirs(clip_dir, exist_ok=True)

# 分辨率（每度像素数）
pix_per_deg = 128

def convert_img_to_tif(lbl_path, tif_path):
    cmd = [
        "gdal_translate",
        "-of", "GTiff",
        lbl_path, tif_path
    ]
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="裁剪TIF文件")
    parser.add_argument("src", type=str, help="lbl文件路径")
    parser.add_argument("tgt", type=str, help="tgt文件路径")
    args = parser.parse_args()
    lbl_path = args.src
    # 输出的 tif 文件名基于 lbl 文件名
    tif_path = args.tgt
    # clip_path = os.path.join(clip_dir, fname.replace('.lbl', '_clip.tif'))
    
    print(f"处理: lbl={lbl_path} -> tif={tif_path}")
    # 将 lbl 文件路径传递给转换函数
    convert_img_to_tif(lbl_path, tif_path)