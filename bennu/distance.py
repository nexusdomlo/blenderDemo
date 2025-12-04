import bpy, math
import bmesh

obj = bpy.context.active_object
mesh = obj.data
mesh.calc_loop_triangles()
T = len(mesh.loop_triangles)  # 三角形数量
R = 246.0  # Bennu 半径 (m) —— 如有不同请修改
S = 4 * math.pi * R * R
A_avg = S / T
a_equilateral = ( (4 * A_avg) / (3**0.5) )**0.5
print(f"Triangles: {T}")
print(f"Surface area ~ {S:.0f} m^2, avg tri area {A_avg:.4f} m^2")
print(f"Estimated mean edge (equilateral approx): {a_equilateral:.3f} m")
bm = bmesh.new()
bm.from_mesh(mesh)

edge_lengths = [e.calc_length() for e in bm.edges]
avg_length = sum(edge_lengths) / len(edge_lengths)
print(f"平均边长: {avg_length} 米")
bm.free()
short_edges = [l for l in edge_lengths if l < 1.0]
print(f"小于1米的边数量: {len(short_edges)}，占比: {len(short_edges)/len(edge_lengths)*100:.2f}%")



