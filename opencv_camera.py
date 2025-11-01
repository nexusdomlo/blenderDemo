# import numpy as np
# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D

# # 相机原点
# O = np.array([0, 0, 0])
# # 定义坐标轴长度
# axis_len = 10
# # X轴（红色，右）
# X = np.array([axis_len, 0, 0])
# # Y轴（绿色，下）
# Y = np.array([0, axis_len, 0])
# # Z轴（蓝色，前）
# Z = np.array([0, 0, axis_len])
# fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')
# # 绘制坐标轴
# ax.quiver(O[0], O[1], O[2], X[0], X[1], X[2], color='r')
# ax.quiver(O[0], O[1], O[2], Y[0], Y[1], Y[2], color='g')
# ax.quiver(O[0], O[1], O[2], Z[0], Z[1], Z[2], color='b')


# # --- Add pixel plane ---
# f = 1  # Focal length, you can adjust
# img_w, img_h = 3, 2  # Pixel plane size
# # Four corners of the pixel plane at Z=f
# corners = np.array([
#     [0, 0, f],             # top-left
#     [img_w, 0, f],         # top-right
#     [img_w, img_h, f],     # bottom-right
#     [0, img_h, f],         # bottom-left
#     [0, 0, f]              # close the loop
# ])
# ax.plot(corners[:,0], corners[:,1], corners[:,2], 'k-', label='pixel plane')
# # Draw u (right) and v (down) axes on pixel plane
# ax.quiver(0, 0, f, 1, 0, 0, color='orange', length=1, normalize=True)
# ax.text(1, 0, f+2, 'u (right)', color='orange')
# ax.quiver(0, 0, f, 0, 1, 0, color='purple', length=1, normalize=True)
# ax.text(0, 1, f+2, 'v (down)', color='purple')
# # Mark pixel plane origin
# ax.scatter(0, 0, f, color='magenta')
# ax.text(0, 0, f+2, '(0,0)', color='magenta')


# # --- Projection demonstration ---
# # 1. 世界坐标系下的点
# Pw = np.array([2, 1, 8])  # (Xw, Yw, Zw)
# ax.scatter(*Pw, color='cyan', s=60, label='World Point $P_w$')
# ax.text(*Pw, '$P_w$', color='cyan')
# # 2. 相机外参（R=I, t=0）
# R = np.eye(3)
# t = np.zeros((3, 1))
# # 3. 相机内参
# K = np.array([
#     [3, 0, 0],
#     [0, 3, 0],
#     [0, 0, 1]
# ])
# # 4. 世界点转到相机坐标系
# Pc = R @ Pw.reshape(3,1) + t  # shape (3,1)
# Pc = Pc.flatten()
# # 5. 归一化像平面坐标
# x_norm = Pc[0] / Pc[2]
# y_norm = Pc[1] / Pc[2]
# # 6. 投影到像素平面
# p_img = K @ np.array([x_norm, y_norm, 1])
# u, v = p_img[0], p_img[1]
# # 7. 在像素平面上画出投影点
# proj_pt = np.array([u, v, f])
# ax.scatter(*proj_pt, color='red', s=60, label='Projection $P\'$')
# ax.text(*proj_pt, "$P'$", color='red')
# # 8. 画投影射线
# ax.plot([Pw[0], proj_pt[0]], [Pw[1], proj_pt[1]], [Pw[2], proj_pt[2]], 'm:', linewidth=1)


# # 设置图例和范围
# ax.set_xlim([-axis_len, axis_len])
# ax.set_ylim([-axis_len, axis_len])
# ax.set_zlim([-axis_len, axis_len])
# ax.set_xlabel('X (right)')
# ax.set_ylabel('Y (down)')
# ax.set_zlabel('Z (forward)')
# ax.set_title('OpenCV camera coordinate system')
# # ax.legend()
# ax.view_init(elev=24, azim=11, roll=92)
# plt.show()

import cv2
import numpy as np

# 你的图片文件路径
image_path = '/mnt/c/Application/1.png'

# 定义一个鼠标回调函数
def get_pixel_coordinates(event, x, y, flags, param):
    # 如果鼠标左键被按下
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"Pixel Coordinates (u, v): ({x}, {y})")

# 读取图片
image = cv2.imread(image_path)
if image is None:
    print(f"Error: Could not read image from {image_path}")
else:
    # 创建一个窗口并绑定鼠标回调函数
    cv2.namedWindow('Image')
    cv2.setMouseCallback('Image', get_pixel_coordinates)

    print("Click on the image to get pixel coordinates. Press 'q' to quit.")

    while True:
        # 显示图片
        cv2.imshow('Image', image)
        
        # 等待按键，如果按下'q'则退出循环
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 关闭所有窗口
    cv2.destroyAllWindows()