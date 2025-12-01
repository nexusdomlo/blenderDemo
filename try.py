import cv2
import numpy as np
import math
import argparse
import tifffile  # 导入 tifffile 库
image = tifffile.imread("C:\Users\MushOtter\Pictures\ldem_polar_75s_30m_000_020.tif")
output_image = cv2.transpose(image)
output_image = cv2.flip(output_image, 1)
tifffile.imwrite("C:\Users\MushOtter\Pictures\output.tif", output_image)