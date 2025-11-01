import bpy # type: ignore
import math


# ...existing code...
import mathutils

def add_great_circle_curve(lat1, lon1, lat2, lon2, R, distance1=0, distance2=0, num_points=32, name='GreatCirclePath'):
    def latlon_to_xyz(lat, lon, r):
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)
        x = r * math.cos(lat_rad) * math.cos(lon_rad)
        y = r * math.cos(lat_rad) * math.sin(lon_rad)
        z = r * math.sin(lat_rad)
        return mathutils.Vector((x, y, z))

    def slerp(p0, p1, t):
        omega = p0.angle(p1)
        if omega == 0:
            return p0
        return (math.sin((1-t)*omega) * p0 + math.sin(t*omega) * p1) / math.sin(omega)

    A = latlon_to_xyz(lat1, lon1, R)
    B = latlon_to_xyz(lat2, lon2, R)
    points = []
    for i in range(num_points):
        t = i / (num_points - 1)
        # 距离球面距离线性插值
        distance = (1 - t) * distance1 + t * distance2
        pt = slerp(A, B, t).normalized() * (R + distance)
        points.append(pt)

    curve_data = bpy.data.curves.new(name, type='CURVE')
    curve_data.dimensions = '3D'
    polyline = curve_data.splines.new('POLY')
    polyline.points.add(len(points)-1)
    for i, pt in enumerate(points):
        polyline.points[i].co = (pt.x, pt.y, pt.z, 1)
    curve_obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(curve_obj)
    return curve_obj




def xyz_to_latlon(x, y, z):
    r = math.sqrt(x**2 + y**2 + z**2)
    lat = math.degrees(math.asin(z / r))
    lon = math.degrees(math.atan2(y, x))
    return lat, lon

# 经纬度范围
lat_min, lat_max = 0, 75
lon_min, lon_max = 180, 200

# 取消所有对象的隐藏状态，避免检测不到，导致没有办法清楚对象
for obj in bpy.data.objects:
    obj.hide_set(False)
# 清空场景
if bpy.context.active_object:
    bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 添加一个半径为17.35的UV球
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=173.8, 
    location=(0, 0, 0), 
    segments=180,      # 段数
    ring_count=120     # 环数
)
# uv_sphere.hide_set(True)  # 在视图中隐藏球体
# uv_sphere.hide_render=True # 在渲染中隐藏球体

# 把UV球当作obj
uv_sphere = bpy.context.active_object 
mesh = uv_sphere.data
bpy.context.view_layer.objects.active = uv_sphere
bpy.ops.object.shade_smooth()
# 示例：在球面上添加一条大圆弧路径
# 假设你的球半径为17.35，A点(0,0)，B点(75,20)，距离球面1米

# 创建或获取顶点组
group_name = "Selected_Faces_Group"
if group_name not in uv_sphere.vertex_groups:
    vgroup = uv_sphere.vertex_groups.new(name=group_name)
else:
    vgroup = uv_sphere.vertex_groups[group_name]

# 进入编辑模式并取消所有选择
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.object.mode_set(mode='OBJECT')

selected_verts = set()

# 选中目标区域的面，并收集顶点
for poly in mesh.polygons:
    co = uv_sphere.matrix_world @ poly.center
    lat, lon = xyz_to_latlon(co.x, co.y, co.z)
    if lon < 0:
        lon += 360
    if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
        poly.select = True
        for vidx in poly.vertices:
            selected_verts.add(vidx)

# 将顶点加入顶点组
if selected_verts:
    vgroup.add(list(selected_verts), 1.0, 'ADD')


# 回到编辑模式，细分选中面
# 进入编辑模式
bpy.ops.object.mode_set(mode='EDIT')
# 切换到顶点选择模式
bpy.ops.mesh.select_mode(type="VERT")
# 取消所有选择
bpy.ops.mesh.select_all(action='DESELECT')
# 选中顶点组
bpy.ops.object.vertex_group_set_active(group=group_name)
bpy.ops.object.vertex_group_select()
# 细分选中区域
bpy.ops.mesh.subdivide(number_cuts=5)
# 返回物体模式
bpy.ops.object.mode_set(mode='OBJECT')




# 添加多级精度（Multiresolution）修改器
# multires_modifier = uv_sphere.modifiers.new(name="Multires", type='MULTIRES')
# # 可选：细分几次
# bpy.context.view_layer.objects.active = uv_sphere
# bpy.ops.object.multires_subdivide(modifier="Multires", mode='CATMULL_CLARK')
# bpy.ops.object.multires_subdivide(modifier="Multires", mode='CATMULL_CLARK')
# 你可以多次调用上面这行以增加细分层级

# 可以暂时不运行置换修改器和材质添加，让其运行脚本快一点
# 添加细分修改器
subdiv_modifier = uv_sphere.modifiers.new(name="Subdivision", type='SUBSURF')
subdiv_modifier.levels = 4
# 这两个值到底有什么用呢，为什么要设置2的时候图中有问题，设置4就没问题呢
subdiv_modifier.render_levels = 4
# 添加置换修改器
displace_modifier = uv_sphere.modifiers.new(name="Displace", type='DISPLACE')
disp_tex = bpy.data.textures.new("DisplaceTexture", type='IMAGE')
disp_img_path = "C:/Application/Store/All_moon_128/outputFile/ldem_128_float_small_masked.png"
disp_img = bpy.data.images.load(disp_img_path)
disp_tex.image = disp_img
displace_modifier.texture = disp_tex
# 设置坐标为UV
displace_modifier.texture_coords = 'UV'
# 设置方向为法向
displace_modifier.direction = 'NORMAL'
# 设置强度
displace_modifier.strength = 10
# 设置中间值，设置为中间值为0.5，那么基本上相比之前大小不变的地方就不会有变化，如果设置为0，那么形变就是在原来的基础上向外形变
displace_modifier.mid_level = 0

# 添加材质
mat = bpy.data.materials.new(name="PlaneMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
nodes.clear()
output = nodes.new(type='ShaderNodeOutputMaterial')
bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
tex_image = nodes.new(type='ShaderNodeTexImage')
img_path = "C:/Application/Store/All_moon_128/outputFile/lroc_color_poles_16k_center180.tif"
img = bpy.data.images.load(img_path)
tex_image.image = img
links.new(tex_image.outputs['Color'], bsdf.inputs['Base Color'])
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
uv_sphere.data.materials.append(mat)


# 添加一个半径为173.8的UV球，用作路径的参照物体
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=173.8, 
    location=(0, 0, 0), 
    segments=180,      # 段数
    ring_count=120     # 环数
)
reference_uv_sphere = bpy.context.active_object

# 隐藏一下UV球
reference_uv_sphere.hide_set(True)  # 在视图中隐藏球体
reference_uv_sphere.hide_render=True # 在渲染中隐藏球体
nurbs_path = add_great_circle_curve(0, 180, 75, 200, 173.8, 13.07, 0.0934+5)
nurbs_path.data.use_path = True
nurbs_path.data.path_duration = 2880
nurbs_path.data.keyframe_insert(data_path="eval_time", frame=1)
nurbs_path.data.keyframe_insert(data_path="eval_time", frame=2880) 

# 添加空物体作为相机的观测目标
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
target = bpy.context.active_object
target.name = "CameraTarget"
# 为观测月球添加摄像机
bpy.ops.object.camera_add()
camera = bpy.context.active_object
camera.rotation_euler = (0, 0, 0)
bpy.context.scene.camera = camera
camera.data.sensor_width = 11.26  # 例如设置为11.26mm
camera.data.sensor_fit = 'AUTO'  # 或 'HORIZONTAL'/'VERTICAL'
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
# 确保激活相机
bpy.context.view_layer.objects.active = camera  
# 设置相机的跟随路径约束
constraint = camera.constraints.new(type='FOLLOW_PATH')
constraint.target = nurbs_path
# 让摄像机沿路径移动（插入偏移关键帧）
constraint.use_fixed_location = True  # 使用固定位置（Blender 2.8+推荐）
constraint.offset_factor = 0.0
constraint.keyframe_insert(data_path="offset_factor", frame=1)
constraint.offset_factor = 1.0
constraint.keyframe_insert(data_path="offset_factor", frame=2880)
# 为相机添加 Track To 约束
track_constraint = camera.constraints.new(type='TRACK_TO')
track_constraint.target = target           # 目标对象
track_constraint.track_axis = 'TRACK_NEGATIVE_Z'  # 追踪轴 -Z
track_constraint.up_axis = 'UP_Y'          # 向上轴 Y

# 添加日光（太阳光源）
bpy.ops.object.light_add(type='SUN', location=(-865, -865, 1220))
sun = bpy.context.active_object
sun.data.energy = 1         # 设置强度
sun.data.angle = 0.526 * math.pi / 180  # 设置角度（度转弧度）
sun.data.color = (1, 1, 1)    # 设置颜色为白色
sun.data.use_shadow = True    # 开启阴影
#修改太陽光方向
sun.rotation_euler = (math.radians(0), math.radians(0), math.radians(0))
# 为相机添加 Track To 约束
track_constraint = sun.constraints.new(type='TRACK_TO')
track_constraint.target = camera           # 目标对象
track_constraint.track_axis = 'TRACK_NEGATIVE_Z'  # 追踪轴 -Z
track_constraint.up_axis = 'UP_Y'          # 向上轴 Y

scene.frame_set(1)

scene.frame_start = 1
scene.frame_end = 2880

# # 拍摄100张照片
# num_photos = 100
# frames = [round(1 + i * (scene.frame_end - 1) / (num_photos - 1)) for i in range(num_photos)]

# scene.render.image_settings.file_format = 'PNG'
# scene.render.filepath = "/your/output/folder/frame_"  # 末尾不要加扩展名

# for idx, f in enumerate(frames):
#     scene.frame_set(f)
#     scene.render.filepath = f"/your/output/folder/frame_{idx+1:03d}.png"
#     bpy.ops.render.render(write_still=True)

# 通过缩囊添加的路径
# 添加路径
# bpy.ops.curve.primitive_nurbs_path_add(location=(0, 0, 0))
# nurbs_path = bpy.context.active_object
# nurbs_path.location = (-17.375,-2, 9.7)
# nurbs_path.rotation_euler = (math.radians(0), math.radians(90), math.radians(0))
# nurbs_path.scale = (4.344, 1, 1)
# curve = nurbs_path.data
# curve.use_path = True
# curve.path_duration = 200  # 让路径动画持续200帧
# curve.eval_time = 1
# curve.keyframe_insert(data_path="eval_time", frame=1)
# curve.eval_time = 200
# curve.keyframe_insert(data_path="eval_time", frame=200) 

# # 给路径添加吸附修改器，吸附到一个参考球面上
# pathShrinkwrapModifier= nurbs_path.modifiers.new(name="pathShrinkwrap", type='SHRINKWRAP')
# pathShrinkwrapModifier.target = reference_uv_sphere
# pathShrinkwrapModifier.wrap_method = 'NEAREST_SURFACEPOINT'  # 最近的表面点
# pathShrinkwrapModifier.wrap_mode = 'ON_SURFACE'              # 吸附模式：表面
# pathShrinkwrapModifier.offset = 5 # 设置偏移为2米
# # 应用路径的修改器
# for mod in nurbs_path.modifiers:
#     bpy.ops.object.modifier_apply(modifier=mod.name)


