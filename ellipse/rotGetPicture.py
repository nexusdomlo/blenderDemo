import bpy # type: ignore
import math
import mathutils # type: ignore
import os
import time
import numpy as np # type: ignore

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

def setup_camera_and_render(
    sensor_width,
    focal_length,
    resolution_x,
    resolution_y,
    output_dir,
    target_location=(0, 0, 0),
    camera_location=(0, 0, 0),
    camera_rotation=(0, 0, 0),
    end_time=7200,
    nurbs_path=None
):
    # 添加空物体作为相机的观测目标
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=target_location)
    target = bpy.context.active_object
    target.name = "CameraTarget"

    # 添加摄像机
    bpy.ops.object.camera_add(location=camera_location, rotation=camera_rotation)
    camera = bpy.context.active_object
    bpy.context.scene.camera = camera
    camera.data.sensor_width = sensor_width
    camera.data.sensor_fit = 'AUTO'
    camera.data.type = 'PERSP'
    camera.data.lens = focal_length
    camera.data.clip_start = 0.1
    camera.data.clip_end = 500000

    # 设置渲染输出属性
    scene = bpy.context.scene
    scene.render.resolution_x = resolution_x
    scene.render.resolution_y = resolution_y
    scene.render.resolution_percentage = 100
    scene.render.pixel_aspect_x = 1.0
    scene.render.pixel_aspect_y = 1.0
    scene.render.fps = 24
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
    scene.render.compositor_device = 'GPU'
    scene.render.compositor_denoise_device = 'GPU'
    scene.render.compositor_denoise_preview_quality = 'FAST'
    scene.render.compositor_denoise_final_quality = 'HIGH'
    os.makedirs(output_dir, exist_ok=True)
    return camera,scene,target

def rotate_object_z(obj, frame_start, frame_end, angle_degree=360):
    """
    让指定物体在 frame_start 到 frame_end 帧，绕 Z 轴旋转 angle_degree 度
    """
    obj.rotation_euler[2] = 0
    obj.keyframe_insert(data_path="rotation_euler", frame=frame_start, index=2)
    obj.rotation_euler[2] = math.radians(angle_degree)
    obj.keyframe_insert(data_path="rotation_euler", frame=frame_end, index=2)
    # 设置为线性插值，保证匀速旋转
    action = obj.animation_data.action
    for fcurve in action.fcurves:
        if fcurve.data_path == "rotation_euler" and fcurve.array_index == 2:
            for kf in fcurve.keyframe_points:
                kf.interpolation = 'LINEAR'


sensor_width = 36  # 传感器宽度，单位毫米ine
focal_length = 838.3  # 焦距，单位毫米
OUTPUT_DIR = "/tmp/ellipse_rot_camera"
picture_count=20
camera_location=(330000, 0, 0)  # 相机位置
end_time = picture_count  # 结束时间，单位秒
nurbs_path = None  # 如果有NURBS路径，可以在这里指定

clean_scene(whiteList=['67p'])

#设计相机的部分
camera,scene,target=setup_camera_and_render(
    sensor_width=sensor_width,
    focal_length=focal_length,
    resolution_x=3840,
    resolution_y=3840,
    output_dir=OUTPUT_DIR,
    camera_location=camera_location,
    camera_rotation=(0, 0, 0),
    end_time=end_time,
    nurbs_path=nurbs_path
)

# 确保激活相机
bpy.context.view_layer.objects.active = camera 

# 为相机添加 Track To 约束
track_constraint = camera.constraints.new(type='TRACK_TO')
track_constraint.target = target           # 目标对象
track_constraint.track_axis = 'TRACK_NEGATIVE_Z'  # 追踪轴 -Z
track_constraint.up_axis = 'UP_Y'          # 向上轴 Y


sun = add_sun_light(
    location=(0, 0, 0),
    energy=1,
    angle_deg=0.526,
    color=(1, 1, 1),
    rotation_euler=(90, 0, 120)
)

# 示例用法
plane = bpy.data.objects['67p']  # 替换为你的物体名称
# 设置场景的帧范围,准备拍摄渲染
scene.frame_start = 1
scene.frame_end = end_time

rotate_object_z(plane, scene.frame_start, scene.frame_end)

# 加1是因为python是左闭右开区间
for frame in range(scene.frame_start, scene.frame_end + 1):
    scene.frame_set(frame)
    # 设置输出文件名
    scene.render.filepath = os.path.join(OUTPUT_DIR, f"frame_{frame:04d}.png")
    bpy.ops.render.render(write_still=True)