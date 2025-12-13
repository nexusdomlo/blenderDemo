import numpy as np
from osgeo import gdal

ds = gdal.Open("D:\\Moon\\0_45_0_90\\0_45_0_45\\ldem_512_0.0n_45.0n_0.0_45.0.tif")
arr = ds.ReadAsArray().astype(np.float32)
# arr = np.flipud(arr)  # 根据需要翻转数组
arr.tofile("D:\\Moon\\0_45_0_90\\0_45_0_45\\ldem_512_0.0n_45.0n_0.0_45.0.bin")  # 直接保存为 float32 二进制文件