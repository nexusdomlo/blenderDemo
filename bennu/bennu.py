import bpy  # type: ignore
import math
start_frame = 0
end_frame = 240
obj_path = r"D:\Asteroid\BENNU\Bennu_asteroid_obj_with_texture\Bennu_texture_obj_flip\test1_rotate_translate.obj"  # 修改为你的实际路径
# 1. 清空场景（可选）
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
# 设置旋转驱动器的函数
def setup_rotation_driver(obj,start_frame,end_frame):
    """
    为物体的Z轴旋转添加一个驱动器，以实现匀速旋转。
    """
    if obj is None:
        print("错误：没有选中的物体。")
        return

    # 确保物体的旋转模式是欧拉角XYZ，这是最直观的
    obj.rotation_mode = 'XYZ'

    # 为Z轴旋转创建一个新的驱动器
    driver = obj.driver_add('rotation_euler', 2) # 2代表Z轴 (X=0, Y=1, Z=2)
    
    # 设置驱动器类型为脚本表达式
    driver.driver.type = 'SCRIPTED'
    
    # 设置驱动器表达式
    # 公式: (当前帧 / 转一圈所需帧数) * 2 * PI
    # 2 * PI 是一整圈的弧度 (360度)
    driver.driver.expression = f"((frame-{start_frame})/ ({end_frame}) - 1/100)* 2 * {math.pi}"  
    # 1/100是为了进行一小部分的偏移，让0度经纬都刚好位于星形的岩石簇
    # 2*pi是为了让物体转一圈，固定部分，我们就别改了
    print(f"成功为物体 '{obj.name}' 的Z轴旋转添加了驱动器。他将以动画的始末刚刚好旋转一圈")
    
def add_sun_light(
    location=(0, 0, 0),
    energy=1,
    angle_deg=0.526,
    color=(1, 1, 1),
    rotation_euler=(30, -90, 0)
):
    """
    添加太阳光（日光源）并设置参数
    :param location: 太阳光位置
    :param energy: 光照强度
    :param angle_deg: 光源角度（度）
    :param color: 光源颜色 (R,G,B)
    :param rotation_euler: 欧拉角（度），如(30, -90, 0)
    :return: sun对象
    """
    bpy.ops.object.light_add(type='SUN', location=location)
    sun = bpy.context.active_object
    sun.data.energy = energy
    sun.data.angle = math.radians(angle_deg)
    sun.data.color = color
    sun.data.use_shadow = True
    sun.rotation_euler = tuple(math.radians(a) for a in rotation_euler)

    # 为太阳光添加 Track To 约束
    # sun_track_constraint = sun.constraints.new(type='TRACK_TO')
    # sun_track_constraint.target = camera           # 目标对象
    # sun_track_constraint.track_axis = 'TRACK_NEGATIVE_Z'  # 追踪轴 -Z
    # sun_track_constraint.up_axis = 'UP_Y'          # 向上轴 Y

    return sun

def import_model(obj_path,x, y, z, rot_x, rot_y, rot_z, scale_x, scale_y, scale_z):
    # 2. 导入 Bennu 的 OBJ 模型
    # bpy.ops.import_scene.obj(filepath=obj_path)
    bpy.ops.wm.obj_import(filepath=obj_path)
    # 3. 获取导入的对象
    imported_objs = [obj for obj in bpy.context.selected_objects]
    if imported_objs:
        model = imported_objs[0]
    else:
        model = bpy.context.active_object  # 兜底

    # 4. 设置位置参数
    model.location = (x, y, z)  # 位置 (x, y, z)
    model.rotation_euler = (rot_x, rot_y, rot_z)  # 旋转 (绕 x, y, z 轴，单位为弧度)
    model.scale = (scale_x, scale_y, scale_z)  # 缩放
    return model

clean_scene(whiteList=['Camera', 'Light'])
bennu_obj=import_model(obj_path,22.506, 8.247,1.21,0.0, 0.0, math.radians(-3.5),26.5, 26.22, 26.7)
# 设置旋转动画
active_obj = bennu_obj
scene = bpy.context.scene
# 场景帧从0开始 ，避免1从240开始导致的240帧动画转不到1圈的问题
scene.frame_set(0)
scene.frame_start = 0
scene.frame_end = end_frame
setup_rotation_driver(active_obj,start_frame,end_frame)
bpy.context.view_layer.update()

print("Bennu 模型已导入并设置旋转动画。")
print("Bennu 模型已导入并设置位置。")

#设置相机
setup_camera(
    sensor_width=8,
    focal_length=20.0,
    resolution_x=1024,
    resolution_y=1024,
    fps=24,
    clip_start=0.1,
    clip_end=1000000,
    camera_type='PERSP',
    nurbs_path=None,
    target=None,
    camera_location=(410, 0, 0),
    camera_rotation=(math.radians(90), 0, math.radians(90))
)

add_sun_light(
    location=(0, 0, 0),
    energy=1,
    angle_deg=0.53,
    color=(1, 1, 1),
    rotation_euler=(0, 90, 0)
)