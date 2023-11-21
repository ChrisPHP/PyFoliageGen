import numpy as np
import lsystem
import pymesh

def calculate_normal(vertices, faces):
    normals = np.zeros((len(vertices), 3), dtype=float)

    for face in faces:
        v1 = np.array(vertices[face[0] - 1])
        v2 = np.array(vertices[face[1] - 1])
        v3 = np.array(vertices[face[2] - 1])

        # Calculate the normal vector for the triangular face
        normal = np.cross(v2 - v1, v3 - v1)

        # Accumulate the normal vectors for each vertex of the face
        for vertex_index in face:
            normals[vertex_index - 1] += normal

    # Normalize the accumulated normal vectors
    for i in range(len(normals)):
        norm_magnitude = np.linalg.norm(normals[i])
        if norm_magnitude < 1e-6:
            # Set a default normal vector (e.g., [0, 0, 1])
            normals[i] = np.array([0, 0, 1], dtype=np.float32)
        else:
            # Normalize the normal vector
            normals[i] /= norm_magnitude

    return normals


def generate_cube_obj(file_path, mesh):
    vertices = mesh.vertices
    faces = mesh.faces
    normals = calculate_normal(vertices=vertices, faces=faces)

    # Write OBJ file
    with open(file_path + '.obj', 'w') as obj_file:
        obj_file.write("# Cube\n")
        obj_file.write("usemtl cube_material\n")

        # Write vertices
        for vertex, normal in zip(vertices, normals):
            obj_file.write("v {} {} {}\n".format(*vertex))
            obj_file.write("vn {} {} {}\n".format(*normal))

        # Write faces
        for face in faces:
            obj_file.write("f {}/{}/{} {}/{}/{} {}/{}/{}\n".format(
                face[0]+1, face[0]+1, face[0]+1,
                face[1]+1, face[1]+1, face[1]+1,
                face[2]+1, face[2]+1, face[2]+1
            ))

    # Write MTL file
    with open(file_path + '.mtl', 'w') as mtl_file:
        mtl_file.write("# Material for Cube\n")
        mtl_file.write("newmtl cube_material\n")
        mtl_file.write("Ka 0.0 1.0 0.0\n")
        mtl_file.write("Kd 0.6 0.6 0.6\n")
        mtl_file.write("Ks 0.9 0.9 0.9\n")
        mtl_file.write("Ns 20\n")

if __name__ == "__main__":
    lsys = lsystem.Lsystem()
    output = lsys.create_lsystem(5, "X")
    meshes = lsys.draw_lsystem(instructions=output, angle=20, distance=2)
    merged_mesh = pymesh.merge_meshes(meshes)
    mesh, info = pymesh.collapse_short_edges(merged_mesh, 0.1)
    mesh, info = pymesh.remove_duplicated_vertices(mesh, 0.1)
    mesh, info = pymesh.remove_duplicated_faces(mesh)
    generate_cube_obj("tree", mesh)