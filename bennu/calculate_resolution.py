import open3d as o3d
import numpy as np
import sys

def analyze_mesh_statistics(file_path):
    """
    分析一个3D网格模型的分辨率统计信息，包括最小、最大和平均边长。

    参数:
    file_path (str): .obj 文件的路径。
    """
    print(f"正在加载模型: {file_path}...")
    
    try:
        # 1. 加载网格模型
        mesh = o3d.io.read_triangle_mesh(file_path)
        
        if not mesh.has_triangles():
            print("错误：模型加载失败或不包含任何三角形面。")
            return
            
        print("模型加载成功。开始计算边长统计信息...")

        # 2. 获取顶点和三角形面
        vertices = np.asarray(mesh.vertices)
        triangles = np.asarray(mesh.triangles)
        
        # 创建一个列表来存储所有边的长度
        edge_lengths = []
        
        # 3. 遍历所有三角形，计算边长
        for triangle in triangles:
            p1, p2, p3 = vertices[triangle]
            
            # 计算并添加三条边的长度到列表中
            edge_lengths.append(np.linalg.norm(p1 - p2))
            edge_lengths.append(np.linalg.norm(p2 - p3))
            edge_lengths.append(np.linalg.norm(p3 - p1))
            
        if not edge_lengths:
            print("错误：模型中没有找到任何边。")
            return

        # 4. 计算最小、最大和平均值
        min_length = np.min(edge_lengths)
        max_length = np.max(edge_lengths)
        avg_length = np.mean(edge_lengths)
        
        print("\n--- 分辨率统计分析结果 ---")
        print(f"模型中的顶点数: {len(vertices)}")
        print(f"模型中的三角形面数: {len(triangles)}")
        print(f"总边数 (三角形数 * 3): {len(edge_lengths)}")
        print("---------------------------------")
        print(f"最高分辨率 (最短边长): {min_length:.8f} 个单位")
        print(f"最低分辨率 (最长边长): {max_length:.8f} 个单位")
        print(f"平均分辨率 (平均边长): {avg_length:.8f} 个单位")
        print("---------------------------------")

    except Exception as e:
        print(f"处理过程中发生错误: {e}")

if __name__ == "__main__":
    # --- 请在这里修改为您的 .obj 文件路径 ---
    model_path = "D:\\Asteroid\\BENNU\\Bennu_model_no_texture\\v20\\Bennu_v20_200k.stl"
    
    if model_path == "path/to/your/model.obj":
        print("错误：请先在脚本中修改 'model_path' 为您的 .obj 文件实际路径。")
        sys.exit(1)
        
    analyze_mesh_statistics(model_path)
