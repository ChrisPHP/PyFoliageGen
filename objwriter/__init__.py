from pymesh import Mesh
import numpy as np
import random

from . import textures

class Objwriter:
    def create_independent_faces(self, faces, max_verts):
        """This function make sure each object is using the correct
           faces.
        """
        updated_faces = []
        for f in faces:
            diff_f1 = max_verts + f[0]
            diff_f2 = max_verts + f[1]
            diff_f3 = max_verts + f[2]
            updated_faces.append([diff_f1, diff_f2, diff_f3])
        return updated_faces

    def generate_obj(self, file_path: str, mesh: Mesh, leaves: Mesh = None):
        """This function creates the obj file for the L-system. It seperates the leaves
           from the main stem making them seperate objs and can apply seperate textures
        """

        vertices = mesh.vertices
        faces = mesh.faces
        max_verts = mesh.num_vertices

        # Write OBJ file
        with open('output/'+file_path + '.obj', 'w') as obj_file:
            obj_file.write("# Tree\n")
            obj_file.write("g main_stem\n")
            obj_file.write("o stem\n")
            obj_file.write("usemtl stem_material\n")

            # Write vertices
            for vertex in vertices:
                obj_file.write("v {} {} {}\n".format(*vertex))

            # Write faces
            for face in faces:
                obj_file.write("f {}/{}/{} {}/{}/{} {}/{}/{}\n".format(
                    face[0]+1, face[0]+1, face[0]+1,
                    face[1]+1, face[1]+1, face[1]+1,
                    face[2]+1, face[2]+1, face[2]+1
                ))

            if  leaves != None:
                obj_file.write("\n")
                obj_file.write("g leaves\n")
                index = 0
                for leaf in leaves:
                    index += 1
                    rand_texture = random.randrange(0, 5)
                    obj_file.write("usemtl leaf_material-{}\n".format(rand_texture))
                    obj_file.write("\n")
                    obj_file.write(f"o leaf-{index}\n")
                    obj_file.write("\n")

                    leaf_vertices = leaf.vertices
                    leaf_faces = self.create_independent_faces(leaf.faces, max_verts)
                    max_verts += leaf.num_vertices

                    # Write vertices
                    for vertex in leaf_vertices:
                        obj_file.write("v {} {} {}\n".format(*vertex))

                    # Write faces
                    for face in leaf_faces:
                        obj_file.write("f {}/{}/{} {}/{}/{} {}/{}/{}\n".format(
                            face[0]+1, face[0]+1, face[0]+1,
                            face[1]+1, face[1]+1, face[1]+1,
                            face[2]+1, face[2]+1, face[2]+1
                    ))

    def generate_mtl(self, file_path: str):
        """This function creates the mtl file for the l-system tree
        """

        txt = textures.Textures()
        leaf_colours = txt.get_palette_colours()

        # Write MTL file
        with open("output/"+file_path + '.mtl', 'w') as mtl_file:
            mtl_file.write("# Material for Tree\n")
            mtl_file.write("newmtl stem_material\n")
            mtl_file.write("Ka 0.4 0.5 0.3\n")
            mtl_file.write("Kd 0.4 0.3 0.2\n")
            mtl_file.write("Ks 1.0 1.0 1.0\n")
            mtl_file.write("illum 1\n")

            index = 0
            for leaf in leaf_colours:
                mtl_file.write("newmtl leaf_material-{}\n".format(index))
                mtl_file.write("Ka 0.0 0.0 0.0\n")
                mtl_file.write("Kd {} {} {}\n".format(leaf[0], leaf[1], leaf[2]))
                mtl_file.write("Ks 0.0 0.0 0.0\n")
                #mtl_file.write("d 0.5\n")
                mtl_file.write("Ns 50\n")
                #mtl_file.write("Ke 1.0, 1.0, 1.0\n")
                index += 1

    def calculate_normal(self, vertices, faces):
        """Unused function to calculate the vertex nomrals
        """
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