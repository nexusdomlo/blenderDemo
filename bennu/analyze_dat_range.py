import struct
import os
import math

# --- 配置 ---
# 输入的 .dat 文件名 (确保和你的文件名一致)
dat_filename = "D:\\Asteroid\\BENNU\\Bennu_Dat\\20190701_ola_scil2Aid04000_v002.dat"

# 根据 XML 文件定义的数据结构 (与你的 convertDat.py 脚本一致)
RECORD_LENGTH_BYTES = 186
X_OFFSET = 115 - 1
Y_OFFSET = 123 - 1
Z_OFFSET = 131 - 1

# --- 主程序 ---

def analyze_dat_file_range(dat_path):
    """
    读取 OLA .dat 文件并计算点云的XYZ范围。
    """
    print(f"开始分析二进制文件: {dat_path}")
    
    if not os.path.exists(dat_path):
        print(f"错误: 文件 '{dat_path}' 不存在。")
        return

    # 初始化最小和最大坐标
    min_x, min_y, min_z = math.inf, math.inf, math.inf
    max_x, max_y, max_z = -math.inf, -math.inf, -math.inf
    point_count = 0

    try:
        with open(dat_path, 'rb') as f_in:
            while True:
                record = f_in.read(RECORD_LENGTH_BYTES)
                if not record:
                    break  # 文件结束

                if len(record) < RECORD_LENGTH_BYTES:
                    continue

                # 解包出 X, Y, Z 坐标
                x = struct.unpack_from('<d', record, X_OFFSET)[0]
                y = struct.unpack_from('<d', record, Y_OFFSET)[0]
                z = struct.unpack_from('<d', record, Z_OFFSET)[0]
                
                # 更新最小和最大值
                min_x = min(min_x, x)
                max_x = max(max_x, x)
                min_y = min(min_y, y)
                max_y = max(max_y, y)
                min_z = min(min_z, z)
                max_z = max(max_z, z)
                
                point_count += 1
                if point_count % 500000 == 0:
                    print(f"已分析 {point_count} 个点...")

    except Exception as e:
        print(f"处理过程中发生错误: {e}")
        return

    if point_count == 0:
        print("文件中没有找到任何点。")
        return

    print(f"\n分析完成！")
    print(f"总共分析了 {point_count} 个点。")
    print("\n--- 点云覆盖范围 (单位: 米) ---")
    print(f"X 轴范围: 从 {min_x:.3f} 到 {max_x:.3f} (跨度: {max_x - min_x:.3f} 米)")
    print(f"Y 轴范围: 从 {min_y:.3f} 到 {max_y:.3f} (跨度: {max_y - min_y:.3f} 米)")
    print(f"Z 轴范围: 从 {min_z:.3f} 到 {max_z:.3f} (跨度: {max_z - min_z:.3f} 米)")


if __name__ == '__main__':
    analyze_dat_file_range(dat_filename)