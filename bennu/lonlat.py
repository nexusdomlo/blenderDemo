import bpy
import math
from mathutils import Vector

def place_object_on_surface(bennu_obj, lon_deg, lat_deg, new_obj_name="Marker", new_obj_size=0.01):
    """
    根据经纬度，在不规则物体表面上放置一个新的物体。

    Args:
        bennu_obj (bpy.types.Object): Bennu的模型对象。
        lon_deg (float): 经度 (-180 to 180 or 0 to 360)。
        lat_deg (float): 纬度 (-90 to 90)。
        new_obj_name (str): 新创建的标记物体的名称。
        new_obj_size (float): 标记物体的大小。
    """
    if bennu_obj is None:
        print(f"错误: 找不到名为 '{BENNU_OBJECT_NAME}' 的Bennu模型。")
        return

    # --- 1. 将经纬度转换为笛卡尔坐标方向向量 ---
    # 假设Bennu模型已对齐：Z轴为自转轴，X轴指向本初子午线
    lon_rad = math.radians(lon_deg)
    lat_rad = math.radians(lat_deg)

    x = math.cos(lat_rad) * math.cos(lon_rad)
    y = math.cos(lat_rad) * math.sin(lon_rad)
    z = math.sin(lat_rad)
    
    direction_vector = Vector((x, y, z))
    print(f"经纬度 ({lon_deg}°, {lat_deg}°) 对应的方向向量: {direction_vector}")

    # --- 2. 执行光线投射 (Ray Casting) ---
    # 我们从Bennu的中心（世界原点）沿着方向向量发射光线
    origin = Vector((0, 0, 0))
    
    # depsgraph是必要的，以确保我们使用的是物体最终的、应用了所有修改器的网格
    depsgraph = bpy.context.evaluated_depsgraph_get()
    bennu_eval = bennu_obj.evaluated_get(depsgraph)

    # 执行光线投射
    # object.ray_cast(origin, direction)
    # 注意：因为我们的原点在物体内部，所以需要从物体自身的坐标系进行投射
    # 我们需要将世界坐标的原点和方向转换为物体的局部坐标
    inv_matrix = bennu_obj.matrix_world.inverted()
    local_origin = inv_matrix @ origin
    local_direction = inv_matrix.to_3x3() @ direction_vector
    
    hit, location, normal, face_index = bennu_eval.ray_cast(local_origin, local_direction)

    # --- 3. 如果找到交点，则放置物体 ---
    if hit:
        # 将返回的局部坐标交点转换回世界坐标
        world_location = bennu_obj.matrix_world @ location
        print(f"光线击中表面！世界坐标位置: {world_location}")

        # 创建一个新的球体作为标记
        bpy.ops.mesh.primitive_uv_sphere_add(radius=new_obj_size, location=world_location)
        marker = bpy.context.active_object
        marker.name = new_obj_name
        
        # --- （可选）为标记添加一个发光的红色材质，使其更显眼 ---
        mat = bpy.data.materials.new(name=f"{new_obj_name}_Material")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        principled_bsdf = nodes.get('Principled BSDF')
        if principled_bsdf:
            principled_bsdf.inputs['Base Color'].default_value = (1, 0, 0, 1)  # 红色
            principled_bsdf.inputs['Emission'].default_value = (1, 0, 0, 1)    # 红色自发光
            principled_bsdf.inputs['Emission Strength'].default_value = 5.0   # 发光强度
        
        marker.data.materials.append(mat)
        
        return marker
    else:
        print("错误: 光线未能击中Bennu模型表面。请检查模型是否在原点，以及方向是否正确。")
        return None

# --- 配置 ---
if __name__ == "__main__":
    # 1. 在这里输入你的Bennu模型在Blender场景中的名字
    BENNU_OBJECT_NAME = "test1_rotate_translate"  # <-- 修改这里！

    # 2. 输入你想要放置物体的经纬度
    longitude_deg = 0.0   # 0° 经线 (本初子午线)
    latitude_deg = 0.0    # 0° 纬线 (赤道)
    
    # 另一个例子：OSIRIS-REx的采样点Nightingale的大致位置
    # longitude_deg = 46.0
    # latitude_deg = 56.0

    # 3. 获取Bennu对象
    bennu_model = bpy.data.objects.get(BENNU_OBJECT_NAME)

    # 4. 执行放置
    place_object_on_surface(bennu_model, longitude_deg, latitude_deg, new_obj_name="Test_Marker")
