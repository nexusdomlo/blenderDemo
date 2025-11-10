import subprocess
import argparse
#裁剪lroc，月球表面材质图

# 原始tif路径和输出路径
input_tif = "D:\\All_moon_128\\outputFile\\lroc_color_poles.tif"


# 可自由修改的经纬度范围
# lon_min = 0
# lon_max = 90
# lat_min = -75 
# lat_max = -60



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="裁剪TIF文件")
    parser.add_argument("lon_min", type=float, help="裁剪经度最小值")
    parser.add_argument("lon_max", type=float, help="裁剪经度最大值")
    parser.add_argument("lat_min", type=float, help="裁剪纬度最小值")
    parser.add_argument("lat_max", type=float, help="裁剪纬度最大值")
    args = parser.parse_args()
    output_tif = f"D:\\All_moon_128\\outputFile\\lroc_color_poles_{int(-args.lat_min)}s_{int(-args.lat_max)}s_{int(args.lon_min)}_{int(args.lon_max)}_.tif"
    
    # tif的像素尺寸
    width = 27360
    height = 13680

    # 经纬度转像素
    xoff = int((args.lon_min + 180) / 360 * width)
    xsize = int((args.lon_max + 180) / 360 * width) - xoff
    yoff = int((90 - args.lat_max) / 180 * height)
    ysize = int((90 - args.lat_min) / 180 * height) - yoff

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