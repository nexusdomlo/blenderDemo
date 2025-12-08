import bpy # type: ignore
import numpy as np # type: ignore
from mathutils import Vector # type: ignore
from bpy_extras.object_utils import world_to_camera_view # type: ignore

# 添加一个全局计数器用于调试
DEBUG_COUNTER = 0

def preprocess_normals():
    """
    预处理函数：计算所有相关网格的平均法线，并将其存储为自定义属性。
    这个函数只需要运行一次。
    """
    root_obj = bpy.data.objects.get("Octree_Root")
    if not root_obj:
        print("预处理错误: 未找到 'Octree_Root'。")
        return

    meshes_to_process = [obj for obj in bpy.data.objects if obj.type == 'MESH' and root_obj in obj.users_collection]
    
    print("开始预处理模型法线...")
    for obj in meshes_to_process:
        if not obj.data.polygons:
            continue
            
        # 计算局部空间中的平均法线
        avg_normal = Vector((0.0, 0.0, 0.0))
        for poly in obj.data.polygons:
            avg_normal += poly.normal
        avg_normal.normalize()
        
        # 将计算结果存储在物体的自定义属性中
        obj["avg_local_normal"] = avg_normal
        print(f"  - 为 '{obj.name}' 存储了平均法线: {avg_normal}")
    print("法线预处理完成。")

def is_in_view(obj, cam, scene):
    """
    检查一个物体是否在相机视锥体内。
    这个版本修复了当相机在包围盒内部时的判断逻辑。
    """
    """
    检查一个物体是否在相机视锥体内，并加入了背面剔除逻辑。
    """
    print("===================================================================")
    bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    # 将8个顶点投影到相机的2D视图上
    coords_2d = [world_to_camera_view(scene, cam, corner) for corner in bbox_corners]
    if(obj.name=="0_45_45_90"):
        print(f"调试: 物体 '{obj.name}' 的包围盒顶点 (世界坐标): {[str(corner) for corner in bbox_corners]}")
        print(f"调试: 物体 '{obj.name}' 的投影坐标 (归一化): {[str(c) for c in coords_2d]}")
    print("===================================================================")
    
    # 1. 检查所有顶点是否都在相机后面 (近裁剪面之外)
    if all(c.z < 0 for c in coords_2d):
        return False
    face1=[coords_2d[2],coords_2d[3],coords_2d[4],coords_2d[5],coords_2d[6],coords_2d[7]]
    # 2. 检查所有顶点是否都在视锥体的同一侧 (左/右/上/下)
    # 只有当所有点都在视锥体外部的同一侧时，物体才完全不可见。
    
    # 检查是否所有点都在右侧 (x > 1)
    if all(c.x > 1 for c in face1):
        return False
        
    # 检查是否所有点都在左侧 (x < 0)
    if all(c.x < 0 for c in face1):
        return False
        
    # 检查是否所有点都在上侧 (y > 1)
    if all(c.y > 1 for c in face1):
        return False
        
    # 检查是否所有点都在下侧 (y < 0)
    if all(c.y < 0 for c in face1):
        return False

    return True


def calculate_distance(obj, camera):
    """计算物体中心点到相机位置的距离"""
    obj_pos = obj.matrix_world.to_translation()
    cam_pos = camera.matrix_world.to_translation()
    return (obj_pos - cam_pos).length

def lod_update(scene):
    """
    [调试版本]
    每一帧更新时调用的主函数。
    """
    print("-" * 40) # 打印分隔符，方便查看每一帧的输出
    cam = scene.camera
    if not cam:
        print("调试: 未找到相机。")
        return
    # --- 关键调试信息 ---
    print(f"调试: 脚本正在使用的相机是: '{cam.name}'")
    # --------------------
    root_obj = bpy.data.objects.get("Octree_Root")
    if not root_obj:
        print("调试: 未找到名为 'Octree_Root' 的根物体。")
        return

    # 1. 收集所有需要处理的网格物体
    meshes_to_process = []
    nodes_to_visit = [root_obj]

    while nodes_to_visit:
        current_node = nodes_to_visit.pop()
        for child in current_node.children:
            if child.type == 'MESH':
                meshes_to_process.append(child)
            elif child.type == 'EMPTY':
                nodes_to_visit.append(child)
    
    if not meshes_to_process:
        print("调试: 在 'Octree_Root' 下未找到任何网格(MESH)物体。请检查层级结构。")
        return
    
    print(f"调试: 找到 {len(meshes_to_process)} 个网格物体进行处理。")

    # 2. 对所有收集到的网格物体进行统一的可见性判断
    for mesh_child in meshes_to_process:
        is_visible = is_in_view(mesh_child, cam, scene)
        
        # 打印每个物体的判断结果
        print(f"  - 物体: '{mesh_child.name}', 是否在视野内: {is_visible}")

        if is_visible:
            if mesh_child.hide_viewport:
                mesh_child.hide_viewport = False
            if mesh_child.hide_render:
                mesh_child.hide_render = False
        else:
            if not mesh_child.hide_viewport:
                mesh_child.hide_viewport = True
            if not mesh_child.hide_render:
                mesh_child.hide_render = True

def register():
    unregister()
    bpy.app.handlers.depsgraph_update_post.append(lod_update)
    print("LOD Handler Registered (Real-time).")

def unregister():
    try:
        bpy.app.handlers.depsgraph_update_post.remove(lod_update)
        print("LOD Handler Unregistered.")
    except (ValueError, AttributeError):
        pass

if __name__ == "__main__":
    # 彻底重启前，先注销一次，确保干净
    unregister()
    # --- 新增：在这里调用预处理函数 ---
    print("="*20 + " 正在执行预处理 " + "="*20)
    preprocess_normals()
    print("="*20 + " 预处理完成 " + "="*20)
    # ------------------------------------
    register()
    # 首次运行时手动调用一次以立即生效
    if bpy.context.scene:
        lod_update(bpy.context.scene)
