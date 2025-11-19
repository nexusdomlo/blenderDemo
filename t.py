# import bpy
# import bmesh
# from mathutils import Vector

# obj = bpy.context.active_object
# bpy.ops.object.mode_set(mode='EDIT')

# bm = bmesh.from_edit_mesh(obj.data)
# uv_layer = bm.loops.layers.uv.active

# center = Vector((0.5, 0.5))

# # 找到最大半径
# max_r = 0
# for face in bm.faces:
#     for loop in face.loops:
#         uv = loop[uv_layer].uv
#         r = (uv - center).length
#         if r > max_r:
#             max_r = r

# # 拉伸所有UV到正方形边界
# for face in bm.faces:
#     for loop in face.loops:
#         uv = loop[uv_layer].uv
#         direction = (uv - center)
#         if direction.length > 0:
#             direction.normalize()
#             # 让方向最大分量为0.5（即到边界）
#             scale = 0.5 / max(abs(direction.x), abs(direction.y))
#             uv_new = center + direction * scale
#             loop[uv_layer].uv = uv_new
#         else:
#             loop[uv_layer].uv = center  # 中心点保持不变

# bmesh.update_edit_mesh(obj.data)






# ### zhankai mei you dai ma gan jin bu chong


# import bpy
# import bmesh
# from mathutils import Vector

# obj = bpy.context.active_object
# bpy.ops.object.mode_set(mode='EDIT')
# bm = bmesh.from_edit_mesh(obj.data)
# uv_layer = bm.loops.layers.uv.active

# # 计算所有UV点的几何中心
# uvs = [loop[uv_layer].uv.copy() for face in bm.faces for loop in face.loops]
# center_uv = sum(uvs, Vector((0.0, 0.0))) / len(uvs)
# offset = Vector((0.5, 0.5)) - center_uv

# # 所有UV点整体移动到图片中心
# for face in bm.faces:
#    for loop in face.loops:
#        loop[uv_layer].uv += offset

# # 找到最大半径
# center = Vector((0.5, 0.5))
# max_r = max((loop[uv_layer].uv - center).length for face in bm.faces for loop in face.loops)

# # 拉伸所有UV到正方形边界
# for face in bm.faces:
#    for loop in face.loops:
#        uv = loop[uv_layer].uv
#        direction = uv - center
#        if direction.length > 0:
#            scale = 0.5 / max(abs(direction.x), abs(direction.y))
#            uv_new = center + direction * scale
#            loop[uv_layer].uv = uv_new
#        else:
#            loop[uv_layer].uv = center

# bmesh.update_edit_mesh(obj.data)


# import bpy
# import bmesh

# obj = bpy.context.active_object
# bpy.ops.object.mode_set(mode='EDIT')
# bm = bmesh.from_edit_mesh(obj.data)
# uv_layer = bm.loops.layers.uv.active

# # 统计每个UV点被引用的次数
# uv_count = {}
# for face in bm.faces:
#     for loop in face.loops:
#         uv = tuple(loop[uv_layer].uv)
#         uv_count[uv] = uv_count.get(uv, 0) + 1

# # 找到被引用最多的UV点
# max_uv = max(uv_count, key=lambda k: uv_count[k])

# # 选中所有UV点
# for face in bm.faces:
#     for loop in face.loops:
#         loop[uv_layer].select = False

# # 选中连接最多的UV点
# for face in bm.faces:
#     for loop in face.loops:
#         if tuple(loop[uv_layer].uv) == max_uv:
#             loop[uv_layer].select = True

# bmesh.update_edit_mesh(obj.data)


# #选点移动
# import bpy
# import bmesh

# obj = bpy.context.active_object
# bpy.ops.object.mode_set(mode='EDIT')
# bm = bmesh.from_edit_mesh(obj.data)
# uv_layer = bm.loops.layers.uv.active

# # 找到已选中的UV点并移动
# for face in bm.faces:
#     for loop in face.loops:
#         if loop[uv_layer].select:
#             loop[uv_layer].uv.x += 0.5
#             loop[uv_layer].uv.y += 0.0

# bmesh.update_edit_mesh(obj.data)