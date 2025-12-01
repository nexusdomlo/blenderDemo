import sys

def find_obj_center(file_path):
    """
    计算 .obj 文件的几何中心和质心。

    :param file_path: .obj 文件的路径
    """
    vertices = []
    min_coords = [float('inf')] * 3
    max_coords = [float('-inf')] * 3
    sum_coords = [0.0, 0.0, 0.0]

    try:
        with open(file_path, 'r') as f:
            for line in f:
                if line.startswith('v '):
                    parts = line.split()
                    # parts[0] is 'v', parts[1] is x, parts[2] is y, parts[3] is z
                    try:
                        x, y, z = map(float, parts[1:4])
                        
                        # 用于计算质心
                        sum_coords[0] += x
                        sum_coords[1] += y
                        sum_coords[2] += z
                        vertices.append((x, y, z))
                        
                        # 用于计算几何中心
                        min_coords[0] = min(min_coords[0], x)
                        min_coords[1] = min(min_coords[1], y)
                        min_coords[2] = min(min_coords[2], z)
                        max_coords[0] = max(max_coords[0], x)
                        max_coords[1] = max(max_coords[1], y)
                        max_coords[2] = max(max_coords[2], z)

                    except (ValueError, IndexError):
                        # 跳过格式不正确的顶点行
                        continue

        if not vertices:
            print("错误：在文件中没有找到任何顶点。")
            return

        num_vertices = len(vertices)

        # 1. 计算质心 (Centroid)
        centroid = [s / num_vertices for s in sum_coords]
        print(f"找到 {num_vertices} 个顶点。")
        print(f"质心 (Centroid):")
        print(f"  X: {centroid[0]:.6f}")
        print(f"  Y: {centroid[1]:.6f}")
        print(f"  Z: {centroid[2]:.6f}")
        print("-" * 20)

        # 2. 计算几何中心 (Geometric Center)
        geometric_center = [
            (min_coords[0] + max_coords[0]) / 2,
            (min_coords[1] + max_coords[1]) / 2,
            (min_coords[2] + max_coords[2]) / 2
        ]
        print(f"几何中心 (Bounding Box Center):")
        print(f"  X: {geometric_center[0]:.6f}")
        print(f"  Y: {geometric_center[1]:.6f}")
        print(f"  Z: {geometric_center[2]:.6f}")
        print("-" * 20)
        print(f"模型范围 (Min/Max Coords):")
        print(f"  X: [{min_coords[0]:.6f}, {max_coords[0]:.6f}]")
        print(f"  Y: [{min_coords[1]:.6f}, {max_coords[1]:.6f}]")
        print(f"  Z: [{min_coords[2]:.6f}, {max_coords[2]:.6f}]")


    except FileNotFoundError:
        print(f"错误：文件未找到 '{file_path}'")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使用方法: python <脚本名>.py <你的bennu.obj文件路径>")
    else:
        obj_file_path = sys.argv[1]
        find_obj_center(obj_file_path)

# 几何中心 (Geometric Center)：也称为包围盒（Bounding Box）的中心。这是最简单和最常用的方法。它计算出模型在X、Y、Z轴上的最大和最小坐标，然后取其中点。
# 质心 (Centroid)：所有顶点的平均位置。如果模型的顶点分布比较均匀，这个点可以很好地代表其质量中心。