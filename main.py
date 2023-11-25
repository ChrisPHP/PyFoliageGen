import numpy as np
import pymesh
import multiprocessing
import json


import objwriter
import lsystem

def create_tree(name: str, leaf: bool):
    with open('rules.json') as f:
        data = json.load(f)
    rules = data[name]

    lsys = lsystem.Lsystem(rules=rules["rules"])
    obj = objwriter.Objwriter()

    output = lsys.create_lsystem(iterations=5, axiom=rules["axiom"])
    meshes = lsys.draw_lsystem(instructions=output, angle=22, distance=2)

    merged_mesh = pymesh.merge_meshes(meshes)
    mesh, info = pymesh.collapse_short_edges(merged_mesh, 0.1)
    mesh, info = pymesh.remove_duplicated_vertices(mesh, 0.1)
    mesh, info = pymesh.remove_duplicated_faces(mesh)

    if leaf == True:
        mesh = pymesh.convex_hull(mesh)

    obj.generate_obj(file_path=name, mesh=mesh)

if __name__ == "__main__":
    cpu_cores = multiprocessing.cpu_count()
    processes = []

    create_tree(name="cordate_leaf", leaf=True)

    #for x in range(8):
    #    file_name = "tree-"+str(x)
    #    p = multiprocessing.Process(target=create_tree, args=[file_name])
    #    p.start()
    #    processes.append(p)

    #for p in processes:
    #    p.join()
