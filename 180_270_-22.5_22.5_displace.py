import bpy # type: ignore
import math
import mathutils # type: ignore

# 经纬度范围
lat_min, lat_max = -22.5, 22.5
lon_min, lon_max = 180, 225
filepath_texture = "C:\\Application\\Store\\moon_crop_0_45_-22.5_22.5_texture.tif"
filepath_normal = "C:\\Application\\Store\\moon_crop_0_45_-22.5_22.5_norm.tif"

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

def get_camera_latlon(camera, sphere_radius):
    cam_pos = camera.location
    # 相机主光轴方向（世界坐标系下）
    dir = camera.matrix_world.to_quaternion() @ mathutils.Vector((0, 0, -1))
    dir = dir.normalized()
    # 求交点
    # cam_pos + t*dir = 球面上一点，|p| = sphere_radius
    # => |cam_pos + t*dir| = sphere_radius
    # 解一元二次方程
    a = dir.dot(dir)
    b = 2 * cam_pos.dot(dir)
    c = cam_pos.dot(cam_pos) - sphere_radius**2
    delta = b**2 - 4*a*c
    if delta < 0:
        return None  # 没有交点
    t = (-b - math.sqrt(delta)) / (2*a)  # 取较小的t（即相机前方最近的交点）
    p = cam_pos + t * dir
    lat, lon = xyz_to_latlon(p.x, p.y, p.z)
    return lat, lon

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
    segments=360,      # 段数
    ring_count=720     # 环数
)

uv_sphere = bpy.context.active_object 
mesh = uv_sphere.data


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
selected_polys = []


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


# 回到编辑模式，分离选中面
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.separate(type='SELECTED')
bpy.ops.object.mode_set(mode='OBJECT')

# ...前面你的代码...

# 获取分离出来的新对象（通常是最后一个）
uv_sphere_part = [obj for obj in bpy.context.selected_objects if obj != uv_sphere][0]
bpy.context.view_layer.objects.active = uv_sphere_part
# 平滑着色
bpy.ops.object.shade_smooth()
mesh = uv_sphere_part.data

# === 添加材质并贴图 ===
mat = bpy.data.materials.new(name="PlaneMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
nodes.clear()
output = nodes.new(type='ShaderNodeOutputMaterial')
bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
tex_image = nodes.new(type='ShaderNodeTexImage')
img_path = filepath_texture  # 修改为你的图片路径
img = bpy.data.images.load(img_path)
tex_image.image = img
links.new(tex_image.outputs['Color'], bsdf.inputs['Base Color'])
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
uv_sphere_part.data.materials.append(mat)

# 只选中分离出来的新对象
bpy.ops.object.select_all(action='DESELECT')
uv_sphere_part.select_set(True)
bpy.context.view_layer.objects.active = uv_sphere_part

# 进入编辑模式并细分
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.subdivide(number_cuts=2)  # 细分次数可调整
bpy.ops.object.mode_set(mode='OBJECT')

# 确保有UV层
if not mesh.uv_layers:
    print("没有UV层,无法操作")
else:
    uv_layer = mesh.uv_layers.active.data

    # 归一化新对象的UV
    u_min = min([uv.uv.x for uv in uv_layer])
    u_max = max([uv.uv.x for uv in uv_layer])
    v_min = min([uv.uv.y for uv in uv_layer])
    v_max = max([uv.uv.y for uv in uv_layer])

    for uv in uv_layer:
        uv.uv.x = (uv.uv.x - u_min) / (u_max - u_min) if u_max != u_min else 0.0
        uv.uv.y = (uv.uv.y - v_min) / (v_max - v_min) if v_max != v_min else 0.0



# 添加细分修改器
subdiv_modifier = uv_sphere_part.modifiers.new(name="Subdivision", type='SUBSURF')
subdiv_modifier.levels = 3
# 这两个值到底有什么用呢，为什么要设置2的时候图中有问题，设置4就没问题呢
subdiv_modifier.render_levels = 3

# 添加置换修改器
displace_modifier = uv_sphere_part.modifiers.new(name="Displace", type='DISPLACE')
disp_tex = bpy.data.textures.new("DisplaceTexture", type='IMAGE')
disp_img_path = filepath_normal
disp_img = bpy.data.images.load(disp_img_path)
disp_tex.image = disp_img
displace_modifier.texture = disp_tex
# 设置坐标为UV
displace_modifier.texture_coords = 'UV'
# 设置方向为法向
displace_modifier.direction = 'NORMAL'
# 设置强度
displace_modifier.strength = 3  
# 设置中间值，设置为中间值为0.5，那么基本上相比之前大小不变的地方就不会有变化，如果设置为0，那么形变就是在原来的基础上向外形变
displace_modifier.mid_level = 0.5   

# 生成路径
nurbs_path = add_great_circle_curve(lat_min, lon_min, lat_max, lon_max, 173.8, 10,5) # 2.5
nurbs_path.data.use_path = True
nurbs_path.data.path_duration = 2880
nurbs_path.data.keyframe_insert(data_path="eval_time", frame=1)
nurbs_path.data.keyframe_insert(data_path="eval_time", frame=2880) 


#设计相机的部分
# 添加空物体作为相机的观测目标
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
target = bpy.context.active_object
target.name = "CameraTarget"
# 为观测月球添加摄像机
bpy.ops.object.camera_add()
camera = bpy.context.active_object
camera.rotation_euler = (0,  math.radians(90), 0)
bpy.context.scene.camera = camera
camera.data.sensor_width = 20  # 例如设置为11.26mm
camera.data.sensor_fit = 'AUTO'  # 或 'HORIZONTAL'/'VERTICAL'
# 设置相机属性（对应图1）       
camera.data.type = 'PERSP'  # 透视
camera.data.lens = 10  # 焦距设置为10mm，可根据需要调整
# camera.data.angle = math.radians(67.4)  # 视野67.4度
camera.data.clip_start = 0.1    # 近裁剪面
camera.data.clip_end = 1000
# 设置渲染输出属性（对应图2）
scene = bpy.context.scene
scene.render.resolution_x = 1024    
scene.render.resolution_y = 1024
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
#track_constraint = camera.constraints.new(type='TRACK_TO')
#track_constraint.target = target           # 目标对象
#track_constraint.track_axis = 'TRACK_NEGATIVE_Z'  # 追踪轴 -Z
#track_constraint.up_axis = 'UP_Y'          # 向上轴 Y

# 添加太阳光
# 添加日光（太阳光源）
bpy.ops.object.light_add(type='SUN', location=(2000, 680, 0))
sun = bpy.context.active_object
sun.data.energy = 1         # 设置强度
sun.data.angle = 0.526 * math.pi / 180  # 设置角度（度转弧度）
sun.data.color = (1, 1, 1)    # 设置颜色为白色
sun.data.use_shadow = True    # 开启阴影
#修改太陽光方向
sun.rotation_euler = (math.radians(0), math.radians(0), math.radians(0))
# 为太阳光添加 Track To 约束
sun_track_constraint = sun.constraints.new(type='TRACK_TO')
sun_track_constraint.target = camera           # 目标对象
sun_track_constraint.track_axis = 'TRACK_NEGATIVE_Z'  # 追踪轴 -Z
sun_track_constraint.up_axis = 'UP_Y'          # 向上轴 Y

# 设置场景的帧范围,准备拍摄渲染
scene.frame_set(1)
scene.frame_start = 1
scene.frame_end = 2880
uv_sphere.hide_set(True)  # 在视图中隐藏球体
uv_sphere.hide_render=True # 在渲染中隐藏球体


# 拍摄100张照片
# num_photos = 100
# frames = [round(1 + i * (scene.frame_end - 1) / (num_photos - 1)) for i in range(num_photos)]

# for idx, f in enumerate(frames):
#     scene.frame_set(f)
#     scene.render.filepath = f"/your/output/folder/frame_{idx+1:03d}.png"
#     bpy.ops.render.render(write_still=True)