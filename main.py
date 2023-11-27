import numpy as np
import pymesh
import multiprocessing
import json
import argparse

import objwriter
import lsystem

obj = objwriter.Objwriter()

def create_tree(name: str, file_name: str):
    with open('rules.json') as f:
        data = json.load(f)
    rules = data[name]

    if "leaf" in rules:
        lsys = lsystem.Lsystem(rules=rules["rules"], leaf=rules["leaf"])
    else:
        lsys = lsystem.Lsystem(rules=rules["rules"])

    output = lsys.create_lsystem(iterations=5, axiom=rules["axiom"], leaf=False)
    meshes, leaves = lsys.draw_lsystem(instructions=output, angle=22, distance=2)


    merged_mesh = pymesh.merge_meshes(meshes)
    mesh, info = pymesh.collapse_short_edges(merged_mesh, 0.1)
    mesh, info = pymesh.remove_duplicated_vertices(mesh, 0.1)
    mesh, info = pymesh.remove_duplicated_faces(mesh)

    if len(leaves) > 0:
        obj.generate_obj(file_path=file_name, mesh=mesh, leaves=leaves)
    else:
        obj.generate_obj(file_path=file_name, mesh=mesh)


def divide_and_conquer(plants_to_generate: int, name: str, number: str):
    index = number
    for x in range(plants_to_generate):
        index+=1
        file_name = name+"-"+str(index)
        create_tree(name=name, file_name=file_name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a tree.')
    parser.add_argument('--cores', type=int, help='Specify how many cores to use')
    parser.add_argument('--tn', type=str, help='Specify the rule to use from rules.json')
    parser.add_argument('--n', type=int, help='Number of trees/plants to generate')
    args = parser.parse_args()

    cpu_cores = multiprocessing.cpu_count()
    plants_to_generate = 1

    if args.cores is None:
        cpu_cores = 1
    elif cpu_cores >= args.cores:
        cpu_cores = args.cores
    if args.n is not None:
        plants_to_generate = args.n
    if args.tn is None:
        print('Please provide a name for the rule you using from rules.json --tn argument.')

    if cpu_cores > plants_to_generate:
        cpu_cores = plants_to_generate

    initial_chunk_size = plants_to_generate // cpu_cores
    remaining = plants_to_generate % cpu_cores
    chunks = [initial_chunk_size] * cpu_cores
    for i in range(remaining):
        chunks[i] += 1

    processes = []

    index = 0
    for chunk in chunks:
        p = multiprocessing.Process(target=divide_and_conquer, args=[chunk,args.tn,index])
        p.start()
        processes.append(p)
        index += chunk

    for p in processes:
        p.join()

    obj.generate_mtl(file_path=args.tn+"-1")