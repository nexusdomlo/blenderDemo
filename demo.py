import bpy # type: ignore
import math


# 取消所有对象的隐藏状态，避免检测不到，导致没有办法清楚对象
for obj in bpy.data.objects:
    obj.hide_set(False)
# 清空场景
if bpy.context.active_object:
    bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 添加一个半径为2的UV球
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=17.35, 
    location=(0, 0, 0), 
    segments=36,      # 段数
    ring_count=32     # 环数
)
uv_sphere = bpy.context.active_object
uv_sphere.hide_set(True)  # 在视图中隐藏球体
uv_sphere.hide_render=True # 在渲染中隐藏球体

# 添加平面
bpy.ops.mesh.primitive_plane_add(location=(3.03, -17.374, 11.35))
plane = bpy.context.active_object
plane.scale = (3.03,11.35, 1)
plane.rotation_euler = (math.radians(90), 0, 0)

# 添加空物体作为弯曲轴
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, -17.374, 0))
axis = bpy.context.active_object

# 细分平面
bpy.context.view_layer.objects.active = plane
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.subdivide(number_cuts=100)
bpy.ops.object.mode_set(mode='OBJECT')

# 添加平滑着色
bpy.ops.object.shade_smooth()

# 添加日光（太阳光源）
bpy.ops.object.light_add(type='SUN', location=(0, -17.374, 0))
sun = bpy.context.active_object
sun.data.energy = 1         # 设置强度
sun.data.angle = 0.526 * math.pi / 180  # 设置角度（度转弧度）
sun.data.color = (1, 1, 1)    # 设置颜色为白色
sun.data.use_shadow = True    # 开启阴影
#修改太陽光方向
sun.rotation_euler = (math.radians(50), math.radians(0), math.radians(0))

# 添加纬度弯曲修改器
latitudeModifier = plane.modifiers.new(name="latitudeBend", type='SIMPLE_DEFORM')
latitudeModifier.deform_axis = 'X'
latitudeModifier.deform_method = 'BEND'
# blender中角度单位是弧度，所以需要转换
latitudeModifier.angle = math.radians(75)
latitudeModifier.origin = axis
# 添加经度弯曲修改器
longitudeModifier = plane.modifiers.new(name="longitudeBend", type='SIMPLE_DEFORM')
longitudeModifier.deform_axis = 'Z'
longitudeModifier.deform_method = 'BEND'
longitudeModifier.angle = math.radians(20)
longitudeModifier.origin = axis

shrinkwrap_modifier = plane.modifiers.new(name="Shrinkwrap", type='SHRINKWRAP')
shrinkwrap_modifier.target = uv_sphere
shrinkwrap_modifier.wrap_method = 'NEAREST_SURFACEPOINT'  # 最近的表面点
shrinkwrap_modifier.wrap_mode = 'ON_SURFACE'              # 吸附模式：表面

# 添加细分修改器
subdiv_modifier = plane.modifiers.new(name="Subdivision", type='SUBSURF')
subdiv_modifier.levels = 4
# 这两个值到底有什么用呢，为什么要设置2的时候图中有问题，设置4就没问题呢
subdiv_modifier.render_levels = 4

#暂时不运行置换修改器和材质添加，让其运行脚本快一点
# 添加置换修改器
displace_modifier = plane.modifiers.new(name="Displace", type='DISPLACE')
disp_tex = bpy.data.textures.new("DisplaceTexture", type='IMAGE')
disp_img_path = "C:/Users/MushOtter/Desktop/merged_0_75_0_20.png"
disp_img = bpy.data.images.load(disp_img_path)
disp_tex.image = disp_img
displace_modifier.texture = disp_tex
# 设置坐标为UV
displace_modifier.texture_coords = 'UV'
# 设置方向为法向
displace_modifier.direction = 'NORMAL'
# 设置强度
displace_modifier.strength = 0.05
# 设置中间值
displace_modifier.mid_level = 0.5


# 添加材质
mat = bpy.data.materials.new(name="PlaneMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
nodes.clear()
output = nodes.new(type='ShaderNodeOutputMaterial')
bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
tex_image = nodes.new(type='ShaderNodeTexImage')
img_path = "C:/Users/MushOtter/Desktop/merged_0_75_0_20.png"
img = bpy.data.images.load(img_path)
tex_image.image = img
links.new(tex_image.outputs['Color'], bsdf.inputs['Base Color'])
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
plane.data.materials.append(mat)


# 添加路径
bpy.ops.curve.primitive_nurbs_path_add(location=(0, 0, 0))
nurbs_path = bpy.context.active_object
nurbs_path.location = (2, -17.375, 10)
nurbs_path.rotation_euler = (math.radians(0), math.radians(90), math.radians(0))
nurbs_path.scale = (5, 1, 1)
curve = nurbs_path.data
curve.eval_time = 1
curve.keyframe_insert(data_path="eval_time", frame=1)
curve.eval_time = 100
curve.keyframe_insert(data_path="eval_time", frame=100) 
pathLatitudeModifier= nurbs_path.modifiers.new(name="pathLatitudeBend", type='SIMPLE_DEFORM')
pathLatitudeModifier.deform_axis = 'X'
pathLatitudeModifier.deform_method = 'BEND'
pathLatitudeModifier.angle = math.radians(45)
pathLatitudeModifier.origin = axis

pathShrinkwrapModifier= nurbs_path.modifiers.new(name="pathShrinkwrap", type='SHRINKWRAP')
pathShrinkwrapModifier.target = uv_sphere
pathShrinkwrapModifier.wrap_method = 'NEAREST_SURFACEPOINT'  # 最近的表面点
pathShrinkwrapModifier.wrap_mode = 'ON_SURFACE'              # 吸附模式：表面
pathShrinkwrapModifier.offset = 2  # 设置偏移为2米

for mod in nurbs_path.modifiers:
    bpy.ops.object.modifier_apply(modifier=mod.name)

# 添加空物体作为相机的观测目标
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
target = bpy.context.active_object
target.name = "CameraTarget"
# 为观测月球添加摄像机
bpy.ops.object.camera_add()
camera = bpy.context.active_object
camera.rotation_euler = (0, 0, 0)
bpy.context.scene.camera = camera
# 设置相机属性（对应图1）       
camera.data.type = 'PERSP'  # 透视
camera.data.lens_unit = 'FOV'  # 视野单位
camera.data.angle = math.radians(30)  # 视野30度
camera.data.clip_start = 0.1    # 近裁剪面
camera.data.clip_end = 1000
# 设置渲染输出属性（对应图2）
scene = bpy.context.scene
scene.render.resolution_x = 2048
scene.render.resolution_y = 2048
scene.render.resolution_percentage = 100
scene.render.pixel_aspect_x = 1.0
scene.render.pixel_aspect_y = 1.0
scene.render.fps = 24

# 设置相机的跟随路径约束
constraint = camera.constraints.new(type='FOLLOW_PATH')
constraint.target = nurbs_path
# 为相机添加 Track To 约束
track_constraint = camera.constraints.new(type='TRACK_TO')
track_constraint.target = target           # 目标对象
track_constraint.track_axis = 'TRACK_NEGATIVE_Z'  # 追踪轴 -Z
track_constraint.up_axis = 'UP_Y'          # 向上轴 Y


scene.frame_set(1)


# 指定帧渲染
frames_to_render = [1, 10, 20, 30, 40, 50]
for frame in frames_to_render:
   bpy.context.scene.frame_set(frame)
   bpy.ops.render.render(write_still=True)
   filepath = f"C:/Users/MushOtter/Documents/BlenderFile/PictureOutput/camera_frame_{frame}.png"
   bpy.data.images['Render Result'].save_render(filepath)

