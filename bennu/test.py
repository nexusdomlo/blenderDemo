import open3d as o3d
import numpy as np

def analyze_mesh_resolution(file_path):
    """
    分析一个3D网格模型的分辨率。
    分辨率通过计算所有三角形的平均边长来估算。

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
            
        print("模型加载成功。开始计算分辨率...")

        # 2. 获取顶点和三角形面
        vertices = np.asarray(mesh.vertices)
        triangles = np.asarray(mesh.triangles)
        
        total_edge_length = 0
        num_edges = 0
        
        # 3. 遍历所有三角形，计算边长
        for triangle in triangles:
            # 获取三角形的三个顶点索引
            p1_idx, p2_idx, p3_idx = triangle
            
            # 获取顶点坐标
            p1 = vertices[p1_idx]
            p2 = vertices[p2_idx]
            p3 = vertices[p3_idx]
            
            # 计算三条边的长度
            edge1_len = np.linalg.norm(p1 - p2)
            edge2_len = np.linalg.norm(p2 - p3)
            edge3_len = np.linalg.norm(p3 - p1)
            
            # 累加总长度和边数
            total_edge_length += edge1_len + edge2_len + edge3_len
            num_edges += 3
            
        if num_edges == 0:
            print("错误：模型中没有找到任何边。")
            return

        # 4. 计算平均边长
        average_edge_length = total_edge_length / num_edges
        
        print("\n--- 分析结果 ---")
        print(f"模型中的顶点数: {len(vertices)}")
        print(f"模型中的三角形面数: {len(triangles)}")
        print(f"估算的模型分辨率 (平均边长): {average_edge_length:.6f} 个单位")
        print("------------------")

    except Exception as e:
        print(f"处理过程中发生错误: {e}")

if __name__ == "__main__":
    # --- 请在这里修改为您的 .obj 文件路径 ---
    # 例如: model_path = "C:/Users/YourUser/Desktop/bennu_model.obj"
    # 或者: model_path = "models/my_scan.obj"
    model_path = "D:\\Asteroid\\BENNU\\Bennu_model_no_texture\\50x-High_res_right_position.obj"
    
    analyze_mesh_resolution(model_path)
