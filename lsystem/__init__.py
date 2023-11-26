import random
import math
import pymesh
import numpy as np

class Cylinder:
    def __init__(self, base, top):
        self.base = base
        self.top = top

class Lsystem:
    def __init__(self, rules: list, leaf: dict = {}):
        self.rules = rules
        self.leaf = leaf

    def draw_lsystem(self, instructions: str, angle: float, distance: float, start_pos: list = [0,0,0], angles: list = [90, 90]) -> list:
        posx: float = start_pos[0]
        posy: float = start_pos[1]
        posz: float = start_pos[2]
        vertical_angle: float = angles[0]
        horizontal_angle: float = angles[1]
        tropism_bool = False
        stack: list = []
        meshes: list = []
        leaves: list = []
        cylinders: list = []
        for char in instructions:
            if char == "F":
                endposx, endposy, endposz = self.polar_to_cartesian(radian=distance, horizontal_angle=horizontal_angle, vertical_angle=vertical_angle)
                endx = posx + endposx
                endy = posy + endposy
                endz = posz + endposz
                if tropism_bool == True:
                    cylinder = Cylinder(base=[posx, posy, posz], top=[endx, endy, endz])
                    cylinders.append(cylinder)
                else:
                    mesh = pymesh.generate_cylinder(p0=[posx, posy, posz], p1=[endx, endy, endz], r0=0.2, r1=0.2, num_segments=16)
                    meshes.append(mesh)
                posx = endx
                posy = endy
                posz = endz
            elif char == "+":
                vertical_angle += angle
            elif char == "-":
                vertical_angle -= angle
            elif char == "/":
                horizontal_angle += angle
            elif char == "\\":
                horizontal_angle -= angle
            elif char == "[":
                stack.append({'posx': posx, 'posy': posy, 'posz': posz, 'vertical_angle': vertical_angle, 'horizontal_angle': horizontal_angle, 'distance': distance})
            elif char == "]":
                popped = stack[len(stack)-1]
                posx = popped['posx']
                posy = popped['posy']
                posz = popped['posz']
                vertical_angle = popped['vertical_angle']
                horizontal_angle = popped['horizontal_angle']
                distance = popped['distance']
                stack.pop()
            elif char == "<":
                tropism_bool = True
            elif char == ">":
                tropism_bool = False
                tropism_vector = np.array([0, 0, -1])  # Bending downward
                max_position_x = max(cylinder.base[0] for cylinder in cylinders)
                bending_function = lambda position: np.arctan(position[0] / max_position_x)  # Example bending function
                troped = self.apply_tropism(cylinders=cylinders, tropism_vector=tropism_vector, bending_function=bending_function)
                for cyl in troped:
                    mesh = pymesh.generate_cylinder(p0=cyl.base, p1=cyl.top, r0=0.2, r1=0.2, num_segments=16)
                    meshes.append(mesh)
                cylinders = []
            elif char == "L":
                output = self.create_lsystem(5, self.leaf["axiom"], leaf=True)
                leaf, _ = self.draw_lsystem(instructions=output, angle=22, distance=0.5, start_pos=[posx, posy, posz], angles=[vertical_angle, horizontal_angle])
                merged_mesh = pymesh.merge_meshes(leaf)
                mesh = pymesh.convex_hull(merged_mesh)
                leaves.append(mesh)
        return meshes, leaves

    def polar_to_cartesian(self, radian: float, horizontal_angle: float, vertical_angle: float) -> float:
        theta_horizontal = horizontal_angle * math.pi / 180
        theta_vertical = vertical_angle * math.pi / 180
        X = radian * math.cos(theta_vertical)
        Y = radian * math.sin(theta_vertical)
        Z = radian * math.cos(theta_horizontal)
        return X, Y, Z

    def rotate_vector(self, vector, axis, angle):
        axis = axis / np.linalg.norm(axis)
        rotation_matrix = np.array([
            [np.cos(angle) + axis[0]**2 * (1 - np.cos(angle)),
            axis[0] * axis[1] * (1 - np.cos(angle)) - axis[2] * np.sin(angle), 
            axis[0] * axis[2] * (1 - np.cos(angle)) + axis[1] * np.sin(angle)],
            [axis[1] * axis[0] * (1 - np.cos(angle)) + axis[2] * np.sin(angle), 
            np.cos(angle) + axis[1]**2 * (1 - np.cos(angle)),
            axis[1] * axis[2] * (1 - np.cos(angle)) - axis[0] * np.sin(angle)],
            [axis[2] * axis[0] * (1 - np.cos(angle)) - axis[1] * np.sin(angle), 
            axis[2] * axis[1] * (1 - np.cos(angle)) + axis[0] * np.sin(angle), 
            np.cos(angle) + axis[2]**2 * (1 - np.cos(angle))]
        ])
        return np.dot(rotation_matrix, vector)

    def apply_tropism(self, cylinders, tropism_vector, bending_function):
        """
        Apply tropism effect to a list of cylinders.
        """
        for i in range(len(cylinders)-1):
            bending_angle = bending_function(cylinders[i].base)
            if (i > 0):
                cylinders[i].base = cylinders[i-1].top
            else:
                cylinders[i].base = self.rotate_vector(cylinders[i].base, tropism_vector, bending_angle)
            cylinders[i].top = self.rotate_vector(cylinders[i].top, tropism_vector, bending_angle)
        return cylinders


    def apply_rules(self, char: str) -> str:
        newstr: str = ""
        for rule in self.rules:
            for key, value in rule.items():
                if char == key:
                    newstr = value
        if newstr == "":
            newstr = char
        return newstr

    def apply_rules_leaf(self, char: str) -> str:
        newstr: str = ""
        for rule in self.leaf["rules"]:
            for key, value in rule.items():
                if char == key:
                    newstr = value
        if newstr == "":
            newstr = char
        return newstr

    def process_string(self, oldstring: str, leaf: bool) -> str:
        newstr: str = ""
        for char in oldstring:
            if leaf == True:
                newstr = newstr + self.apply_rules_leaf(char=char)
            else:
                newstr = newstr + self.apply_rules(char=char)
        return newstr

    def create_lsystem(self, iterations: int, axiom: str, leaf: bool) -> str:
        startstring: str = axiom
        endstring: str = ""
        for _ in range(iterations):
            endstring = self.process_string(oldstring=startstring, leaf=leaf)
            startstring = endstring
        return endstring