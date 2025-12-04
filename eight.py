import bpy # type: ignore
from mathutils import Vector # type: ignore

# 添加一个全局计数器用于调试
DEBUG_COUNTER = 0

def calculate_distance(obj, camera):
    """计算物体中心点到相机位置的距离"""
    obj_pos = obj.matrix_world.to_translation()
    cam_pos = camera.matrix_world.to_translation()
    return (obj_pos - cam_pos).length

def lod_update(scene):
    """
    每一帧更新时调用的主函数。
    遍历八叉树结构，根据节点与相机的距离来显示或隐藏其下的网格物体。
    """
    # # --- 诊断代码 ---
    # global DEBUG_COUNTER
    # DEBUG_COUNTER += 1
    # print(f"LOD Update 正在运行! 调用次数: {DEBUG_COUNTER}")
    # # --- 诊断代码结束 ---

    cam = scene.camera
    if not cam:
        return

    root_obj = bpy.data.objects.get("Octree_Root")
    if not root_obj:
        return

    visibility_distance = 1000.0

    def process_node(node):
        for child in node.children:
            if child.type == 'EMPTY':
                process_node(child)

        distance_to_node = calculate_distance(node, cam)
        should_be_visible = (distance_to_node <= visibility_distance)
        mesh_children = [child for child in node.children if child.type == 'MESH']

        for mesh_child in mesh_children:
            mesh_child.hide_viewport = not should_be_visible
            mesh_child.hide_render = not should_be_visible
            
    process_node(root_obj)


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
    register()
    lod_update(bpy.context.scene)