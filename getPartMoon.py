import bpy # type: ignore
import math
import mathutils # type: ignore
import os

# 经纬度范围
lat_min, lat_max = -60, 0
lon_min, lon_max = 0, 90
sensor_width=5.632  # 传感器宽度，单位mm
focal_length=4.877      # 焦距，单位mm
height1=150 #起始高度
height2=90 #到南纬30度时的高度
height3=30 #到南纬60度时的高度
height4=1  #到月球表面时的高度
# 计算视场角
fov_rad = 2 * math.atan(sensor_width / (2 * focal_length))
angel_offset1 =math.tan(fov_rad/2)*height1*360/(2*math.pi*1740) # 100km对应的角度偏移
angel_offset2 =math.tan(fov_rad/2)*height2*360/(2*math.pi*1740)  # 50km对应的角度偏移
path_lat_min, path_lat_max = lat_min+angel_offset1, lat_max-angel_offset2
path_lon_min, path_lon_max = lon_min+angel_offset1, lon_max-angel_offset2
end_time=240
OUTPUT_DIR = "C:\\Application\\Moon\\output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 预加载图片资源
preload_images = {}
def preload_image_resources():
    for img_path in [
        # "D:\Moon\lroc_color_poles_8k_30s_00s_00_20.tif",
        # "D:\Moon\lroc_color_poles_8k_45s_30s_00_20.tif",
        # "D:\Moon\lroc_color_poles_8k_60s_45s_00_20.tif",
        # "D:\Moon\lroc_color_poles_8k_75s_60s_00_20.tif",
        "D:\\All_moon_128\\outputFile\\lroc_color_poles_30s_00s_000_090_.tif",
        "D:\\All_moon_128\\outputFile\\lroc_color_poles_60s_30s_000_090_.tif",
        "D:\\Moon\\ldem_256_30s_00s_000_090_float.tif",
        "D:\\Moon\\ldem_256_60s_30s_000_090_float.tif",
        "D:\\Moon\\ldem_512_75s_60s_000_090_float.tif"
    ]:
        if os.path.exists(img_path):
            try:
                preload_images[img_path] = bpy.data.images.load(img_path)
            except Exception as e:
                print(f"[Warn] 图片预加载失败: {img_path}", e)
        else:
            print(f"[Warn] 图片文件不存在: {img_path}")

def xyz_to_latlon(x, y, z):
    r = math.sqrt(x**2 + y**2 + z**2)
    lat = math.degrees(math.asin(z / r))
    lon = math.degrees(math.atan2(y, x))
    return lat, lon

def add_great_circle_curve(lat1, lon1, lat2, lon2, R, distance1=0, distance2=0, num_points=64, name='GreatCirclePath'):
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

def select_and_materialize_region(
    obj, 
    lat_min, lat_max, lon_min, lon_max, 
    texture_path, normal_path, 
    group_name="Selected_Faces_Group",
    scale=1.0,
):
    """
    提取指定经纬度范围的顶点组，并为其添加材质和节点连接
    """
    mesh = obj.data

    # 创建或获取顶点组
    if group_name not in obj.vertex_groups:
        vgroup = obj.vertex_groups.new(name=group_name)
    else:
        vgroup = obj.vertex_groups[group_name]

    # 进入编辑模式并取消所有选择
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')

    selected_verts = set()
    selected_polys = []

    # 选中目标区域的面，并收集顶点
    for poly in mesh.polygons:
        co = obj.matrix_world @ poly.center
        lat, lon = xyz_to_latlon(co.x, co.y, co.z)
        if lon < 0:
            lon += 360
        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            poly.select = True
            for vidx in poly.vertices:
                selected_verts.add(vidx)

    # 回到编辑模式，分离选中面
    bpy.ops.object.mode_set(mode='EDIT')
    pre_objs = set(bpy.context.scene.objects)
    try:
        bpy.ops.mesh.separate(type='SELECTED')
    except Exception as e:
        print("Separate failed:", e)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.view_layer.update()
    post_objs = set(bpy.context.scene.objects)
    new_objs = list(post_objs - pre_objs)
    if new_objs:
        part_obj = new_objs[0]
    else:
        part_obj = obj

    # 获取分离出来的新对象
    bpy.context.view_layer.objects.active = part_obj
    # bpy.ops.object.shade_smooth()
    mesh = part_obj.data

    # === 添加材质并贴图 ===
    mat = bpy.data.materials.new(name="PlaneMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    output = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    tex_image = nodes.new(type='ShaderNodeTexImage')
    disp_image = nodes.new(type='ShaderNodeTexImage')

    # 加载贴图
    if texture_path in preload_images:
        tex_image.image = preload_images[texture_path]
    elif os.path.exists(texture_path):
        try:
            tex_image.image = bpy.data.images.load(texture_path)
        except Exception as e:
            print("[Warn] 加载颜色贴图失败:", e)

    if normal_path in preload_images:
        disp_image.image = preload_images[normal_path]
    elif os.path.exists(normal_path):
        try:
            disp_image.image = bpy.data.images.load(normal_path)
        except Exception as e:
            print("[Warn] 加载置换贴图失败:", e)
    # disp_image.image.colorspace_settings.name = 'Non-Color'
    # 节点连接
    try:
        links.new(tex_image.outputs['Color'], bsdf.inputs['Base Color'])
        links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
        displace = nodes.new(type='ShaderNodeDisplacement')
        displace.location = (200, -100)
        displace.inputs['Midlevel'].default_value = 0.5
        if(normal_path.lower().endswith('.tif')):
            displace.inputs['Scale'].default_value = scale
        else:
            displace.inputs['Scale'].default_value = 6
        links.new(disp_image.outputs['Color'], displace.inputs['Height'])
        links.new(displace.outputs['Displacement'], output.inputs['Displacement'])
    except Exception as e:
        print("[Warn] 材质节点连接失败:", e)
        nodes.clear()
        output = nodes.new(type='ShaderNodeOutputMaterial')
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        links = mat.node_tree.links
        links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    part_obj.data.materials.clear()
    part_obj.data.materials.append(mat)

     # === 细分和UV归一化 ===
    bpy.ops.object.select_all(action='DESELECT')
    part_obj.select_set(True)
    bpy.context.view_layer.objects.active = part_obj

    # 细分
    try:
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        #细分值，可根据需要调整
        bpy.ops.mesh.subdivide(number_cuts=8)
        bpy.ops.object.mode_set(mode='OBJECT')
    except Exception as e:
        print("[Warn] 细分失败:", e)
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except Exception:
            pass

    # UV归一化
    mesh = part_obj.data
    if mesh.uv_layers:
        uv_layer = mesh.uv_layers.active.data
        try:
            u_min = min([uv.uv.x for uv in uv_layer])
            u_max = max([uv.uv.x for uv in uv_layer])
            v_min = min([uv.uv.y for uv in uv_layer])
            v_max = max([uv.uv.y for uv in uv_layer])
            for uv in uv_layer:
                uv.uv.x = (uv.uv.x - u_min) / (u_max - u_min) if u_max != u_min else 0.0
                uv.uv.y = (uv.uv.y - v_min) / (v_max - v_min) if v_max != v_min else 0.0
        except Exception as e:
            print("[Warn] UV 归一化失败:", e)
    else:
        print("[Warn] 没有UV层, 无法操作")
    return part_obj

def setup_camera(
    sensor_width=11.26, 
    focal_length=10.0, 
    resolution_x=1024, 
    resolution_y=1024, 
    fps=24, 
    clip_start=0.1, 
    clip_end=100000,
    camera_type='PERSP',
    nurbs_path=None,
    target=None,
    end_time=240,
    camera_location=(0, 0, 0),
    camera_rotation=(0, 0, 0)
):
    """
    创建并设置相机，添加路径跟随和追踪约束，并设置渲染参数。
    参数：
        sensor_width: 传感器宽度（mm）
        focal_length: 焦距（mm）
        resolution_x, resolution_y: 渲染分辨率
        fps: 帧率
        clip_start, clip_end: 裁剪面
        camera_type: 'PERSP' 或 'ORTHO'
        nurbs_path: 跟随的路径对象
        target: 追踪目标对象
        end_time: 路径动画结束帧
        camera_location, camera_rotation: 相机初始位置和欧拉角
    返回：
        camera: 新建的相机对象
    """
    # 添加相机
    bpy.ops.object.camera_add(location=camera_location, rotation=camera_rotation)
    camera = bpy.context.active_object
    bpy.context.scene.camera = camera
    camera.data.sensor_width = sensor_width
    camera.data.sensor_fit = 'AUTO'
    camera.data.type = camera_type
    camera.data.lens = focal_length
    camera.data.clip_start = clip_start
    camera.data.clip_end = clip_end

    # 设置渲染输出属性
    scene = bpy.context.scene
    scene.render.resolution_x = resolution_x
    scene.render.resolution_y = resolution_y
    scene.render.resolution_percentage = 100
    scene.render.pixel_aspect_x = 1.0
    scene.render.pixel_aspect_y = 1.0
    scene.render.fps = fps

    # 路径跟随约束
    if nurbs_path is not None:
        constraint = camera.constraints.new(type='FOLLOW_PATH')
        constraint.target = nurbs_path
        constraint.use_fixed_location = True
        constraint.offset_factor = 0.0
        constraint.keyframe_insert(data_path="offset_factor", frame=1)
        constraint.offset_factor = 1.0
        constraint.keyframe_insert(data_path="offset_factor", frame=end_time)

    # 追踪目标约束
    if target is not None:
        track_constraint = camera.constraints.new(type='TRACK_TO')
        track_constraint.target = target
        track_constraint.track_axis = 'TRACK_NEGATIVE_Z'
        track_constraint.up_axis = 'UP_Y'

    # 激活相机
    bpy.context.view_layer.objects.active = camera

    return camera

def clean_scene(whiteList=None):
    """
    清空场景，保留白名单中的对象
    :param whitelist: 不清除的对象名称列表，如 ['Camera', 'Light']
    """
    if whiteList is None:
        whiteList = []
    # 取消所有对象的隐藏状态，避免检测不到，导致没有办法清楚对象
    for obj in bpy.data.objects:
        try:
            obj.hide_set(False)
        except Exception:
            pass
    # 清空场景（只选中非白名单对象）
    if bpy.context.active_object:
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except Exception:
            pass
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.objects:
        if obj.name not in whiteList:
            obj.select_set(True)
    bpy.ops.object.delete()

clean_scene()
# 添加一个半径为17.35的UV球
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=1738, 
    location=(0, 0, 0), 
    segments=360,      # 段数
    ring_count=180     # 环数
)
#获得UV球体对象
uv_sphere = bpy.context.active_object 
mesh = uv_sphere.data

# uv_sphere_part1=select_and_materialize_region(uv_sphere, -60, -30, 0, 20, "", "D:\\Moon\\ldem_256_60s_30s_000_020_float.tif", scale=1.0)

# uv_sphere_part2=select_and_materialize_region(uv_sphere, -45, -30, 0, 20, "", "D:\\Moon\\ldem_512_45s_30s_000_020_float.tif",scale=1)

# uv_sphere_part3=select_and_materialize_region(uv_sphere, -60, -45,0, 20, "", "D:\\Moon\\ldem_512_60s_45s_000_020_float.tif",scale=1)

# uv_sphere_part4=select_and_materialize_region(uv_sphere, -75, -60, 0, 20, "", "D:\\Moon\\ldem_1024_75s_60s_000_020.tif",scale=20)
uv_sphere_part5=select_and_materialize_region(uv_sphere, -30, 0, 0, 90, "D:\\All_moon_128\\outputFile\\lroc_color_poles_30s_00s_000_090_.tif", "D:\\Moon\\ldem_256_30s_00s_000_090_float.tif", scale=100)
uv_sphere_part6=select_and_materialize_region(uv_sphere, -60, -30, 0, 90, "D:\\All_moon_128\\outputFile\\lroc_color_poles_60s_30s_000_090_.tif", "D:\\Moon\\ldem_256_60s_30s_000_090_float.tif", scale=100)
uv_sphere_part7=select_and_materialize_region(uv_sphere, -75, -60, 0, 90, "", "D:\\Moon\\ldem_512_75s_60s_000_090_float.tif", scale=100)

#  生成路径
nurbs_path = add_great_circle_curve(path_lat_max, path_lon_max, path_lat_min, path_lon_min,  1738, height1,height2) # 2.5
nurbs_path.data.use_path = True
nurbs_path.data.path_duration = end_time  # 24秒，1440帧
nurbs_path.data.keyframe_insert(data_path="eval_time", frame=1)
nurbs_path.data.keyframe_insert(data_path="eval_time", frame=end_time) 

# 渲染属性的设置
bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'
bpy.context.scene.render.compositor_device = 'GPU'
bpy.context.scene.render.compositor_denoise_device = 'GPU'
bpy.context.scene.render.compositor_denoise_preview_quality = 'FAST'
bpy.context.scene.render.compositor_denoise_final_quality = 'HIGH'

#设计相机的部分
# 1.添加空物体作为相机的观测目标
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
target = bpy.context.active_object
target.name = "CameraTarget"

camera = setup_camera(
    sensor_width=sensor_width,
    focal_length=focal_length,
    resolution_x=1024,
    resolution_y=1024,
    fps=24,
    clip_start=0.1,
    clip_end=100000,
    camera_type='PERSP',
    nurbs_path=nurbs_path,
    target=target,
    end_time=end_time,
    camera_location=(0, 0, 0),
    camera_rotation=(0, 0, 0)
)

# 添加太阳光
# 添加日光（太阳光源）
bpy.ops.object.light_add(type='SUN', location=(0, 0, 0))
sun = bpy.context.active_object
sun.data.energy = 1         # 设置强度
sun.data.angle = 0.526 * math.pi / 180  # 设置角度（度转弧度）
sun.data.color = (1, 1, 1)    # 设置颜色为白色
sun.data.use_shadow = True    # 开启阴影
#修改太陽光方向
sun.rotation_euler = (math.radians(-10), math.radians(127.5), math.radians(0))
# 为太阳光添加 Track To 约束
# sun_track_constraint = sun.constraints.new(type='TRACK_TO')
# sun_track_constraint.target = camera           # 目标对象
# sun_track_constraint.track_axis = 'TRACK_NEGATIVE_Z'  # 追踪轴 -Z
# sun_track_constraint.up_axis = 'UP_Y'          # 向上轴 Y

# 设置场景的帧范围,准备拍摄渲染
scene = bpy.context.scene
scene.frame_set(1)
scene.frame_start = 1
scene.frame_end = end_time
uv_sphere.hide_set(True)  # 在视图中隐藏球体
uv_sphere.hide_render=True # 在渲染中隐藏球体
