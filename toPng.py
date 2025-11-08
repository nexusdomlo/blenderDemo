# import os
# import subprocess

# src_path = r"D:\Moon\ldem_256_60s_30s_000_090_float.tif"
# if not os.path.exists(src_path):
#     raise FileNotFoundError(f"源文件不存在: {src_path}")
# bit16_path = r"D:\Moon\ldem_256_60s_30s_000_090_16bit.tif"
# # 先生成 16-bit GeoTIFF（保留地理参考）
# cmd = [
#     "gdal_translate",
#     "-of", "GTiff",
#     "-ot", "UInt16",
#     "-scale", "-5.4660801887512", "4.4430456161499", "0", "65535",
#     "-a_nodata", "0",
#     src_path,
#     bit16_path
# ]
# subprocess.run(cmd, check=True)
# alpha_path = r"D:\Moon\ldem_256_60s_30s_000_090_16bit_alpha.tif"
# # 为 nodata 加 alpha 通道
# cmd = [
#     "gdalwarp",
#     "-dstalpha",
#     bit16_path,
#     alpha_path
# ]
# subprocess.run(cmd, check=True)

# output_png = r"D:\Moon\ldem_256_60s_30s_000_090_16bit_alpha.png"
# # 转为带 alpha 的 PNG
# cmd = [
#     "gdal_translate",
#     "-of", "PNG",
#     alpha_path,
#     output_png
# ]
# subprocess.run(cmd, check=True)
# #去除中间值
# os.remove(bit16_path)
# os.remove(alpha_path)

# gdal_translate -of PNG -ot UInt16 -scale -5.88241147995 4.8301405906677 0 65535 -a_nodata 0 "D:\Moon\ldem_256_30s_00s_000_090_float.tif" "D:\Moon\ldem_256_30s_00s_000_090_16bit.png"
from osgeo import gdal

src_path = r"D:\Moon\ldem_256_60s_30s_000_090_float.tif"
ds = gdal.Open(src_path)
band = ds.GetRasterBand(1)
stats = band.GetStatistics(True, True)
print(f"最小值: {stats[0]}, 最大值: {stats[1]}")