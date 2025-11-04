import subprocess
#裁剪lroc，月球表面材质图

# 原始tif路径和输出路径
input_tif = r"D:\All_moon_128\outputFile\lroc_color_poles.tif"
output_tif = r"D:\All_moon_128\outputFile\lroc_color_poles_30s_00s_000_090_.tif"

# 可自由修改的经纬度范围
lon_min = 0
lon_max = 90
lat_min = -30
lat_max = 0

# tif的像素尺寸
width = 27360
height = 13680

# 经纬度转像素
xoff = int((lon_min + 180) / 360 * width)
xsize = int((lon_max + 180) / 360 * width) - xoff
yoff = int((90 - lat_max) / 180 * height)
ysize = int((90 - lat_min) / 180 * height) - yoff

# 构造命令
cmd = [
    "gdal_translate",
    "-srcwin", str(xoff), str(yoff), str(xsize), str(ysize),
    input_tif,
    output_tif
]

# 执行命令
subprocess.run(cmd, check=True)
print("裁剪完成，输出文件：", output_tif)