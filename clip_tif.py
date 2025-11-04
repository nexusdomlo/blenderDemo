# import os
# import subprocess
# from osgeo import gdal
# from osgeo import osr # 导入 osr 模块

# def clip_tif_by_lonlat(input_tif_path, output_tif_path, lon_min, lat_min, lon_max, lat_max):
#     """
#     根据经纬度范围裁剪TIFF文件。

#     Args:
#         input_tif_path (str): 输入TIFF文件的路径。
#         output_tif_path (str): 输出裁剪后TIFF文件的路径。
#         lon_min (float): 裁剪区域的最小经度。
#         lat_min (float): 裁剪区域的最小纬度。
#         lon_max (float): 裁剪区域的最大经度。
#         lat_max (float): 裁剪区域的最大纬度。
#     """
#     # 使用 gdal.Warp 进行裁剪
#     # -te 参数的顺序是 minx miny maxx maxy (最小经度, 最小纬度, 最大经度, 最大纬度)
#     print(f"执行裁剪命令: gdal.Warp({output_tif_path}, {input_tif_path}, outputBounds=[{lon_min}, {lat_min}, {lon_max}, {lat_max}])")
#     try:
#         # 获取输入文件的投影信息
#         src_ds = gdal.Open(input_tif_path)
#         if src_ds is None:
#             raise Exception(f"无法打开输入文件: {input_tif_path}")
#         src_srs = src_ds.GetProjection()
#         # 尝试从投影中获取地理坐标系
#         srs = osr.SpatialReference() # 使用 osr 模块
#         srs.ImportFromWkt(src_srs)
#         geog_srs = srs.CloneGeogCS()
#         geog_srs_wkt = geog_srs.ExportToWkt()
#         src_ds = None # 关闭数据集

#         gdal.Warp(output_tif_path, input_tif_path,
#                   srcSRS=src_srs,
#                   outputBounds=[lon_min, lat_min, lon_max, lat_max],
#                   outputBoundsSRS=geog_srs_wkt) # 明确指定 outputBounds 的坐标系
#         print(f"裁剪成功！输出文件: {output_tif_path}")
#     except Exception as e:
#         print(f"裁剪失败: {e}")

# if __name__ == "__main__":
#     # 示例用法
#     input_file = "D:\\Moon\\ldem_256_90s_00s_000_180_float.tif"  # 替换为你的输入TIFF文件路径
#     output_file = "D:\\Moon\\clipped_moon_surface.tif"  # 替换为你的输出TIFF文件路径

#     # 定义裁剪区域 (经度, 纬度)
#     # 注意：对于月球数据，纬度可能从北到南递减，或者南纬为负值。
#     # 根据 gdalinfo 输出，南纬是负值，北纬是正值。
#     # 示例裁剪区域：经度 0 到 20 度，纬度 -60 到 -30 度 (南纬 60 到 30 度)
#     clip_lon_min = 0.0
#     clip_lat_min = -60.0
#     clip_lon_max = 20.0
#     clip_lat_max = -30.0

#     # 确保输出目录存在
#     os.makedirs(os.path.dirname(output_file), exist_ok=True)

#     clip_tif_by_lonlat(input_file, output_file, clip_lon_min, clip_lat_min, clip_lon_max, clip_lat_max)


import os
import subprocess
from osgeo import gdal
from osgeo import osr # 导入 osr 模块

def clip_tif_by_lonlat(input_tif_path, output_tif_path, lon_min, lat_min, lon_max, lat_max):
    """
    根据经纬度范围裁剪TIFF文件。

    Args:
        input_tif_path (str): 输入TIFF文件的路径。
        output_tif_path (str): 输出裁剪后TIFF文件的路径。
        lon_min (float): 裁剪区域的最小经度。
        lat_min (float): 裁剪区域的最小纬度。
        lon_max (float): 裁剪区域的最大经度。
        lat_max (float): 裁剪区域的最大纬度。
    """
    # 使用 gdal.Warp 进行裁剪
    # -te 参数的顺序是 minx miny maxx maxy (最小经度, 最小纬度, 最大经度, 最大纬度)
    print(f"执行裁剪命令: gdal.Warp({output_tif_path}, {input_tif_path}, outputBounds=[{lon_min}, {lat_min}, {lon_max}, {lat_max}])")
    try:
        # 获取输入文件的投影信息
        src_ds = gdal.Open(input_tif_path)
        if src_ds is None:
            raise Exception(f"无法打开输入文件: {input_tif_path}")
        src_srs = src_ds.GetProjection()
        # 尝试从投影中获取地理坐标系
        srs = osr.SpatialReference() # 使用 osr 模块
        srs.ImportFromWkt(src_srs)
        geog_srs = srs.CloneGeogCS()
        geog_srs_wkt = geog_srs.ExportToWkt()
        src_ds = None # 关闭数据集

        result = gdal.Warp(output_tif_path, input_tif_path,
                           srcSRS=src_srs,
                           outputBounds=[lon_min, lat_min, lon_max, lat_max],
                           outputBoundsSRS=geog_srs_wkt) # 明确指定 outputBounds 的坐标系
        if result:
            print(f"裁剪成功！输出文件: {output_tif_path}")
        else:
            raise Exception("gdal.Warp 返回 None，裁剪可能失败。")
    except Exception as e:
        print(f"裁剪失败: {e}")

if __name__ == "__main__":
    # 示例用法
    input_file = "D:\\Moon\\ldem_256_90s_00s_000_180_float.tif"  # 替换为你的输入TIFF文件路径
    output_file = "D:\\Moon\\clipped_moon_surface.tif"  # 替换为你的输出TIFF文件路径

    # 定义裁剪区域 (经度, 纬度)
    # 注意：对于月球数据，纬度可能从北到南递减，或者南纬为负值。
    # 根据 gdalinfo 输出，南纬是负值，北纬是正值。
    # 示例裁剪区域：经度 0 到 20 度，纬度 -60 到 -30 度 (南纬 60 到 30 度)
    clip_lon_min = 0.0
    clip_lat_min = -60.0
    clip_lon_max = 20.0
    clip_lat_max = -30.0

    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    clip_tif_by_lonlat(input_file, output_file, clip_lon_min, clip_lat_min, clip_lon_max, clip_lat_max)
