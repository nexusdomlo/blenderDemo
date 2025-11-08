import os
import subprocess

# 原始影像范围
src_lon_min, src_lon_max = 0, 90
src_lat_min, src_lat_max = 0, 45

# 配置参数
tif_path = r"D:\Moon\ldem_512_00n_45n_000_090_float.tif"       # 输入TIF文件路径
clip_path = r"D:\Moon\ldem_512_00n_45n_000_030_float.tif"      # 裁剪后TIF输出路径
os.makedirs(os.path.dirname(clip_path), exist_ok=True)

# 裁剪区域（经纬度）
lon_min, lon_max = 0, 30      # 经度范围
lat_min, lat_max = 0, 45      # 纬度范围（南纬为负）

# 分辨率（每度像素数）
pix_per_deg = 512

# 计算像素窗口
xoff = int((lon_min - src_lon_min) * pix_per_deg)   # 起始列
yoff = int((src_lat_max - lat_max) * pix_per_deg)   # 起始行（纬度0在顶部，-30在下方）
xsize = int((lon_max - lon_min) * pix_per_deg)
ysize = int(abs(lat_max - lat_min) * pix_per_deg)

# xoff表示横轴偏移量
# yoff表示纵轴偏移量，但是纵轴正方向向下
# xsize表示裁剪宽度
# ysize表示裁剪高度
# 使用srcwin这个参数来裁剪影像，可以直接使用经纬度值
def clip_tif_by_pixel(tif_path, out_path, xoff, yoff, xsize, ysize):
    cmd = [
        "gdal_translate",
        "-srcwin", str(xoff), str(yoff), str(xsize), str(ysize),
        tif_path, out_path
    ]
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    print(f"裁剪: {tif_path}")
    print(f"xoff={xoff}, yoff={yoff}, xsize={xsize}, ysize={ysize}")
    clip_tif_by_pixel(tif_path, clip_path, xoff, yoff, xsize, ysize)