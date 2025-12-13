import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

# is_in_view 函数的逻辑是正确的，我们保持它不变
def is_in_view(obj, cam, scene):
    """
    检查一个物体是否在相机视锥体内。
    这个版本修复了当相机在包围盒内部时的判断逻辑。
    """
    bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    coords_2d = [world_to_camera_view(scene, cam, corner) for corner in bbox_corners]

    if all(c.z <= 0 for c in coords_2d):
        return False

    points_in_front = [c for c in coords_2d if c.z > 0]

    if not points_in_front:
        return True

    min_x = min(c.x for c in points_in_front)
    max_x = max(c.x for c in points_in_front)
    min_y = min(c.y for c in points_in_front)
    max_y = max(c.y for c in points_in_front)

    if max_x < 0 or min_x > 1 or max_y < 0 or min_y > 1:
        return False

    return True


# --- lod_update 函数是修正的核心 ---
def lod_update(scene, depsgraph):
    """
    [最终修正版 + 强制刷新]
    每一帧更新时调用的主函数。
    从依赖关系图(depsgraph)获取最终计算后的对象状态。
    """
    cam_orig = scene.camera
    if not cam_orig: return
        
    cam_eval = cam_orig.evaluated_get(depsgraph)

    root_obj_orig = bpy.data.objects.get("Octree_Root")
    if not root_obj_orig: return
        
    root_obj_eval = root_obj_orig.evaluated_get(depsgraph)

    nodes_to_visit = list(root_obj_eval.children)
    
    # 增加一个标志位，判断本次运行是否做了任何修改
    view_changed = False

    while nodes_to_visit:
        child_eval = nodes_to_visit.pop(0)
        
        if child_eval.type == 'EMPTY':
            nodes_to_visit.extend(child_eval.children)
        
        elif child_eval.type == 'MESH':
            is_visible = is_in_view(child_eval, cam_eval, scene)
            original_mesh_obj = child_eval.original
            
            if original_mesh_obj.hide_viewport == is_visible:
                new_hidden_state = not is_visible
                original_mesh_obj.hide_viewport = new_hidden_state
                original_mesh_obj.hide_render = new_hidden_state
                view_changed = True # 标记发生了变化

    # 【终极解决方案】如果视口中的物体可见性发生了变化，则强制重绘
    if view_changed:
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()


# --- register 和 unregister 函数保持不变 ---
def register():
    unregister()
    bpy.app.handlers.depsgraph_update_post.append(lod_update)
    print("LOD Handler Registered (with forced redraw).")

def unregister():
    for handler in bpy.app.handlers.depsgraph_update_post:
        if handler.__name__ == "lod_update":
            bpy.app.handlers.depsgraph_update_post.remove(handler)
            print("LOD Handler Unregistered.")
            return

if __name__ == "__main__":
    register()
    if bpy.context.scene:
        depsgraph = bpy.context.evaluated_depsgraph_get()
        lod_update(bpy.context.scene, depsgraph)