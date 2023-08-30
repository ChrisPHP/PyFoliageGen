import lsystem
import pymesh
from pywavefront import Wavefront

lsys = lsystem.Lsystem()
output = lsys.create_lsystem(5, "X")
meshes = lsys.draw_lsystem(instructions=output, angle=20, distance=4)
merged_mesh = pymesh.merge_meshes(meshes)
mesh, info = pymesh.collapse_short_edges(merged_mesh, 0.1)
print(info)
mesh, info = pymesh.remove_duplicated_vertices(mesh, 0.1)
print(info)
mesh, info = pymesh.remove_duplicated_faces(mesh)
print(info)
pymesh.save_mesh("tree.obj", mesh)
