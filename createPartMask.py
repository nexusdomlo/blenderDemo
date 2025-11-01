from PIL import Image

# 你的原图
src_img = Image.open("merged_0_75_0_20.png").convert("L")
src_width, src_height = src_img.size

# 全月图尺寸
full_width, full_height = 184320 , 92162

# 经纬度到像素的换算
pixels_per_degree_lon = full_width / 360
pixels_per_degree_lat = full_height / 180

# 你的图片的经纬度范围
lon_start, lon_end = 0, 20
lat_start, lat_end = 0, 75

# 计算粘贴位置（左上角）
x_start = int(lon_start * pixels_per_degree_lon)
y_center = full_height // 2
y_start = int(y_center - lat_end * pixels_per_degree_lat)  # 纬度0在中间，75N在上方

# 创建全黑底图
full_img = Image.new("L", (full_width, full_height), 0)

# 粘贴
full_img.paste(src_img, (x_start, y_start))

# 保存
full_img.save("all_moon_0_20_0_75_mask.png")