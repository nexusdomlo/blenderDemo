import os
import subprocess

# 配置参数
img_dir = "D:\\Moon"      # IMG文件夹路径
tif_dir = "D:\\Moon"      # TIF输出路径
clip_dir = "D:\\Moon"    # 裁剪后TIF输出路径
os.makedirs(tif_dir, exist_ok=True)
os.makedirs(clip_dir, exist_ok=True)

# 裁剪区域（经纬度）
lon_min, lon_max = 0, 20      # 经度范围
lat_min, lat_max = -60, -45     # 纬度范围（南纬为负）

# 分辨率（每度像素数）
pix_per_deg = 256

# 计算像素窗口
xoff = int((lon_min - 0) * pix_per_deg)   # 起始列
yoff = int((0 - lat_min) * pix_per_deg)   # 起始行（纬度0在顶部）
xsize = int((lon_max - lon_min) * pix_per_deg)
ysize = int(abs(lat_max - lat_min) * pix_per_deg)

def convert_img_to_tif(img_path, tif_path):
    cmd = [
        "gdal_translate",
        "-of", "GTiff",
        img_path, tif_path
    ]
    subprocess.run(cmd, check=True)

def clip_tif_by_pixel(tif_path, out_path, xoff, yoff, xsize, ysize):
    cmd = [
        "gdal_translate",
        "-srcwin", str(xoff), str(yoff), str(xsize), str(ysize),
        tif_path, out_path
    ]
    subprocess.run(cmd, check=True)

def batch_process():
    for fname in os.listdir(img_dir):
        if fname.lower().endswith('.img'):
            img_path = os.path.join(img_dir, fname)
            tif_path = os.path.join(tif_dir, fname.replace('.img', '.tif'))
            clip_path = os.path.join(clip_dir, fname.replace('.img', '_clip.tif'))
            print(f"处理: {fname}")
            convert_img_to_tif(img_path, tif_path)
            clip_tif_by_pixel(tif_path, clip_path, xoff, yoff, xsize, ysize)

if __name__ == "__main__":
    batch_process()