import math
import mathutils # type: ignore

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
        distance = (1 - t) * distance1 + t * distance2
        pt = slerp(A, B, t).normalized() * (R + distance)
        points.append(pt)

    import bpy
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