# import cv2
# import numpy as np
# from scipy.spatial.transform import Rotation as R_scipy


# # lat_min, lat_max = -15, 15
# # lon_min, lon_max = 180, 240
# # sensor_width=5.632  # 传感器宽度，单位mm
# # focal_length=4.877      # 焦距，单位mm
# # height1=150
# # height2=150
# # # 计算视场角
# # fov_rad = 2 * math.atan(sensor_width / (2 * focal_length))
# # angel_offset1 =math.tan(fov_rad/2)*height1*360/(2*math.pi*1740) # 100km对应的角度偏移
# # angel_offset2 =math.tan(fov_rad/2)*height2*360/(2*math.pi*1740)  # 50km对应的角度偏移
# world_data = np.load('data/world_points2.npy', allow_pickle=True)
# detected_data = np.load('data/detected_points2.npy', allow_pickle=True)
# print(world_data)
# print(detected_data)
# # 3D点（世界坐标，形状为 Nx3）
# object_points = np.array(world_data, dtype=np.float32)


# # 2D点（像素坐标，形状为 Nx2）
# image_points = np.array(detected_data, dtype=np.float32)

# # 检查点数是否匹配
# assert len(object_points) == len(image_points), "3D点和2D点的数量必须一致"
# assert len(object_points) >= 4, "PnP至少需要4个点"

# # 相机内参矩阵
# K = np.array([
#     [886.72725, 0, 512],
#     [0, 886.72725, 512],
#     [0,  0,  1]
# ], dtype=np.float32)

# # 畸变参数（如无畸变可用np.zeros(5)）
# dist_coeffs = np.zeros(5, dtype=np.float32)

# # 求解PnP
# success, rvec, tvec = cv2.solvePnP(
#     object_points, 
#     image_points, 
#     K, 
#     dist_coeffs,
# )

# if success:
#     # rvec为旋转向量，tvec为平移向量
#     # 可将rvec转为旋转矩阵
#     R, _ = cv2.Rodrigues(rvec)
#     print("旋转矩阵 R:\n", R)
#     rot = R_scipy.from_matrix(R)
#     euler_angles = rot.as_euler('zyx', degrees=True)
#     print("欧拉角 (ZYX, 单位:度):", euler_angles)
#     print("平移向量 t:\n", tvec)
# else:
#     print("PnP求解失败")

# # R_cv, t_cv: PnP得到的旋转矩阵和平移向量
# R_cv, _ = cv2.Rodrigues(rvec)
# t_cv = tvec.flatten()

# # 1. 求逆，得到相机在世界中的位姿
# R_world_cam_cv = R_cv.T
# t_world_cam_cv = -R_cv.T @ t_cv

# # 2. 坐标系转换
# T_blender_cv = np.array([
#     [1, 0,  0],
#     [0, 0, -1],
#     [0, 1,  0]
# ])

# R_world_cam_blender = T_blender_cv @ R_world_cam_cv @ T_blender_cv.T
# t_world_cam_blender = T_blender_cv @ t_world_cam_cv

# # 3. 构建Blender的matrix_world
# import numpy as np
# matrix_world_blender = np.eye(4)
# matrix_world_blender[:3, :3] = R_world_cam_blender
# matrix_world_blender[:3, 3] = t_world_cam_blender
# # 提取 Location 和欧拉角（XYZ顺序，Blender默认）
# location = matrix_world_blender[:3, 3]
# rot = R_scipy.from_matrix(matrix_world_blender[:3, :3])
# euler_xyz_deg = rot.as_euler('xyz', degrees=True)

# print("\n=== 复制到 Blender 的参数 ===")
# print(f"Location (X, Y, Z): {location[0]:.4f}, {location[1]:.4f}, {location[2]:.4f}")
# print(f"Rotation (X, Y, Z, 单位:度): {euler_xyz_deg[0]:.4f}, {euler_xyz_deg[1]:.4f}, {euler_xyz_deg[2]:.4f}")
# print("请在Blender中将相机的旋转模式设置为 'XYZ 欧拉'，然后输入上述数值。")

# # 以下代码用于图像左右交换，将图片中心调整为0度经线
from PIL import Image

img = Image.open("D:\\All_moon_128\\outputFile\\ldem_128_float_small_small.png")
w, h = img.size

# 截取左半边和右半边
left_half = img.crop((0, 0, w//2, h))
right_half = img.crop((w//2, 0, w, h))

# 创建新图片
new_img = Image.new(img.mode, (w, h))

# 将右半边放到左边
new_img.paste(right_half, (0, 0))
# 将左半边放到右边
new_img.paste(left_half, (w//2, 0))

new_img.save("D:\\All_moon_128\\outputFile\\ldem_128_float_small_small_output.png")