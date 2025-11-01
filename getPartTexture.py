# 以经度 [-10, 10]，纬度 [-10, 10] 为例
lon_min, lon_max = -180, -150
lat_min, lat_max = -15, 0

x_off = int((lon_min + 180) / 360 * 27360)
x_end = int((lon_max + 180) / 360 * 27360)
y_off = int((90 - lat_max) / 180 * 13680)
y_end = int((90 - lat_min) / 180 * 13680)

width = x_end - x_off
height = y_end - y_off
print(x_off, y_off, width, height)

# gdal_translate -srcwin x_off y_off width height /mnt/d/Moon/lroc_color_poles_8k.tif output.tif