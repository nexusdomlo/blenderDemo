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
        "C:\\Users\\MushOtter\\Pictures\\ldem_cropped_rect1.png"
        # "D:\\Moon\\ldem_512_75s_60s_000_090_float.tif",
        # "D:\\Moon\\ldem_75s_30m_16bit_alpha.png"
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
        # bpy.ops.mesh.subdivide(number_cuts=1)
        bpy.ops.object.mode_set(mode='OBJECT')
    except Exception as e:
        print("[Warn] 细分失败:", e)
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except Exception:
            pass

    # UV归一化 其实就是拉伸球面映射到整个贴图区域
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
    # === UV展开 ===
    try:
        bpy.context.view_layer.objects.active = part_obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
        bpy.ops.object.mode_set(mode='OBJECT')
        print("UV展开完成")
    except Exception as e:
        print("[Warn] UV展开失败:", e)

    return part_obj


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
preload_image_resources()
img_list = list(preload_images.values())
print("预加载图片数量:", len(img_list))
# uv_sphere_part1=select_and_materialize_region(uv_sphere, -75, -60, 0, 90, 
#                                               "", 
#                                               img_list[0].filepath, 
#                                               scale=100)
uv_sphere_part2=select_and_materialize_region(uv_sphere, -90, -75, 0, 20, 
                                              "", 
                                              img_list[0].filepath,
                                              scale=100)


# 设置场景的帧范围,准备拍摄渲染
scene = bpy.context.scene
scene.frame_set(1)
scene.frame_start = 1
scene.frame_end = end_time
uv_sphere.hide_set(True)  # 在视图中隐藏球体
uv_sphere.hide_render=True # 在渲染中隐藏球体
