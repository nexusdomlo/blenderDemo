import struct
import os

# --- 配置 ---
# 输入的 .dat 文件名 (确保和你的文件名一致)
dat_filename = "D:\\Asteroid\\BENNU\\Bennu_Dat\\20190701_ola_scil2Aid04000_v002.dat"

# 输出的文本文件名
output_filename = "D:\\Asteroid\\BENNU\\Bennu_Dat\\20190701_ola_scil2Aid04000_v002.xyz"

# 根据 XML 文件定义的数据结构
RECORD_LENGTH_BYTES = 186
# X, Y, Z 坐标在每条记录中的起始位置 (从1开始，所以要减1)
X_OFFSET = 115 - 1
Y_OFFSET = 123 - 1
Z_OFFSET = 131 - 1
# 每个坐标占8个字节
FIELD_LENGTH = 8

# --- 主程序 ---

def convert_dat_to_xyz(dat_path, output_path):
    """
    读取 OLA .dat 文件并提取 X, Y, Z 坐标到一个 .xyz 文件。
    """
    print(f"开始读取二进制文件: {dat_path}")
    
    # 检查文件是否存在
    if not os.path.exists(dat_path):
        print(f"错误: 文件 '{dat_path}' 不存在。请确保脚本和.dat文件在同一个文件夹下。")
        return

    point_count = 0
    try:
        with open(dat_path, 'rb') as f_in, open(output_path, 'w') as f_out:
            while True:
                # 读取一条完整的记录
                record = f_in.read(RECORD_LENGTH_BYTES)
                if not record:
                    break  # 文件结束

                # 确保我们读取了完整的记录
                if len(record) < RECORD_LENGTH_BYTES:
                    continue

                # 使用 struct 模块从记录的特定位置解包出 X, Y, Z 坐标
                # '<d' 表示小端（LSB）双精度浮点数 (8字节)
                x = struct.unpack_from('<d', record, X_OFFSET)[0]
                y = struct.unpack_from('<d', record, Y_OFFSET)[0]
                z = struct.unpack_from('<d', record, Z_OFFSET)[0]
                
                # 将坐标写入输出文件，格式为 "X Y Z"
                f_out.write(f"{x} {y} {z}\n")
                
                point_count += 1
                if point_count % 100000 == 0:
                    print(f"已处理 {point_count} 个点...")

    except Exception as e:
        print(f"处理过程中发生错误: {e}")
        return

    print(f"\n转换完成！")
    print(f"总共提取了 {point_count} 个点。")
    print(f"点云数据已保存到: {output_path}")


if __name__ == '__main__':
    convert_dat_to_xyz(dat_filename, output_filename)

