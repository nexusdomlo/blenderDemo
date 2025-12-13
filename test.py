import bpy # type: ignore
from mathutils import Vector # type: ignore
from bpy_extras.object_utils import world_to_camera_view # type: ignore


def is_in_view(obj, cam, scene):
    """
    检查一个物体是否在相机视锥体内。
    这个版本修复了当相机在包围盒内部时的判断逻辑。
    """
    """
    检查一个物体是否在相机视锥体内，并加入了背面剔除逻辑。
    """
    # # --- 新增：背面剔除判断 ---
    # if "avg_local_normal" in obj:
    #     # 1. 获取从相机到物体中心的向量
    #     cam_to_obj_vec = obj.matrix_world.to_translation() - cam.matrix_world.to_translation()
        
    #     # 2. 获取物体在世界空间中的平均法线
    #     #    只旋转，不平移或缩放
    #     world_normal = obj.matrix_world.to_3x3() @ obj["avg_local_normal"]
        
    #     # 3. 计算点积
    #     dot_product = cam_to_obj_vec.dot(world_normal)
        
    #     # 如果点积 > 0，说明相机在物体背面，直接剔除
    #     if dot_product > 0:
    #         return False
    # # --- 背面剔除结束 ---
    # 获取物体在世界坐标系中的8个包围盒顶点
    bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    # 将8个顶点投影到相机的2D视图上
    coords_2d = [world_to_camera_view(scene, cam, corner) for corner in bbox_corners]
    # --- 核心逻辑修正 ---

    # 1. 检查所有顶点是否都在相机后面 (近裁剪面之外)
    if all(c.z < 0 for c in coords_2d):
        return False

    face1=[coords_2d[2],coords_2d[3],coords_2d[4],coords_2d[5],coords_2d[7],coords_2d[6]]
    if all(c.x < 0 for c in face1):
        return False
    if all(c.x > 1 for c in face1):
        return False
    if all(c.y < 0 for c in face1):
        return False
    if all(c.y > 1 for c in face1):
        return False
    # 如果以上剔除条件都不满足，说明物体与视锥体相交，是可见的
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
    print(scene.frame_current)
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
    bpy.app.handlers.frame_change_post.append(lod_update)

    # bpy.app.handlers.depsgraph_update_post.append(lod_update)
    print("LOD Handler Registered (Real-time).")

def unregister():
    try:
        bpy.app.handlers.frame_change_post.remove(lod_update)
        # bpy.app.handlers.depsgraph_update_post.remove(lod_update)
        print("LOD Handler Unregistered.")
    except (ValueError, AttributeError):
        pass

if __name__ == "__main__":
    # 彻底重启前，先注销一次，确保干净
    unregister()
    register()
    # 首次运行时手动调用一次以立即生效
    if bpy.context.scene:
        lod_update(bpy.context.scene)
