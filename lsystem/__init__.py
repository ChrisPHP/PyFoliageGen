import random
import math
import pymesh
import numpy as np
import pyvista as pv

class Cylinder:
    def __init__(self, base, top):
        self.base = base
        self.top = top

class Lsystem:
    def __init__(self, rules: list, start_radius: float = 0.5, end_radius: float = 0.5, leaf: dict = {}):
        self.rules = rules
        self.leaf = leaf
        self.start_radius = start_radius
        self.end_radius = end_radius

    def draw_lsystem(self, instructions: str, distance: float, angle: float, start_pos: list = [0,0,0], angles: list = [90, 90], triangulate: bool = False) -> list:
        """Main function for creating the 3D model for the Lsystem tree.
        """
        posx: float = start_pos[0]
        posy: float = start_pos[1]
        posz: float = start_pos[2]
        vertical_angle: float = angles[0]
        horizontal_angle: float = angles[1]
        start_radius = self.start_radius
        end_radius = self.start_radius
        stack: list = []
        meshes: list = []
        leaves: list = []

        for char in instructions:
            if char == "F":
                bent_angle = self.calculate_bending_angle(elasticity=0.2, angle=9.8, position=[posx, posy, posz], tropism=[0.2, 0.2, 2])
                vertical_angle += bent_angle
                horizontal_angle += bent_angle
                endposx, endposy, endposz = self.polar_to_cartesian(radian=distance, horizontal_angle=horizontal_angle, vertical_angle=vertical_angle)
                endx = posx + endposx
                endy = posy + endposy
                endz = posz + endposz
                if triangulate == True:
                    meshes.append([posx, posy, posz])
                    meshes.append([endx, endy, endz])
                else:
                    mesh = pymesh.generate_cylinder(p0=[posx, posy, posz], p1=[endx, endy, endz], r0=start_radius, r1=end_radius, num_segments=16)
                    meshes.append(mesh)
                posx = endx
                posy = endy
                posz = endz
                if start_radius >= self.end_radius:
                    start_radius -= 0.06
                    end_radius -= 0.06
                elif start_radius != end_radius:
                    end_radius = start_radius
            elif char == "+":
                vertical_angle += angle
            elif char == "-":
                vertical_angle -= angle
            elif char == "/":
                horizontal_angle += angle
            elif char == "\\":
                horizontal_angle -= angle
            elif char == "[":
                stack.append({
                    'posx': posx,
                    'posy': posy,
                    'posz': posz,
                    'vertical_angle': vertical_angle,
                    'horizontal_angle': horizontal_angle,
                    'distance': distance,
                    'start_radius': start_radius,
                    'end_radius': end_radius
                })
            elif char == "]":
                popped = stack[len(stack)-1]
                posx = popped['posx']
                posy = popped['posy']
                posz = popped['posz']
                vertical_angle = popped['vertical_angle']
                horizontal_angle = popped['horizontal_angle']
                distance = popped['distance']
                start_radius = popped['start_radius']
                end_radius = popped['end_radius']
                stack.pop()
            elif char == "L":
                output = self.create_lsystem(5, self.leaf["axiom"], leaf=True)
                leaf, _ = self.draw_lsystem(instructions=output,
                                            distance=1,
                                            angle=20,
                                            start_pos=[posx, posy, posz],
                                            angles=[vertical_angle, horizontal_angle],
                                            triangulate=self.leaf["2d"])
                if self.leaf["2d"]:
                    cloud = pv.PolyData(leaf)
                    surf = cloud.delaunay_2d()
                    surf_points = surf.extract_surface().points

                    mesh = pymesh.form_mesh(surf_points, surf.regular_faces)
                else:
                    merged_mesh = pymesh.merge_meshes(leaf)
                    mesh = pymesh.convex_hull(merged_mesh)

                leaves.append(mesh)
            elif char == "O":
                endposx, endposy, endposz = self.polar_to_cartesian(radian=distance, horizontal_angle=horizontal_angle, vertical_angle=vertical_angle)
                mesh = pymesh.generate_icosphere(distance, [posx, posy, posz])
                meshes.append(mesh)
        return meshes, leaves

    def polar_to_cartesian(self, radian: float, horizontal_angle: float, vertical_angle: float) -> float:
        """Function to convert polar to cartesian coordinates to allow for vertical and
           horizontal angles.
        """
        theta_horizontal = horizontal_angle * math.pi / 180
        theta_vertical = vertical_angle * math.pi / 180
        X = radian * math.cos(theta_vertical)
        Y = radian * math.sin(theta_vertical)
        Z = radian * math.cos(theta_horizontal)
        return X, Y, Z

    def calculate_bending_angle(self, elasticity: float, angle: float, position: list, tropism: list) -> float:
        alpha = math.radians(angle)
        HT_diff = math.sqrt((position[0] - tropism[0])**2 + (position[1] - tropism[1])**2 + (position[2] - tropism[2])**2)
        return elasticity * ((math.cos(alpha) - math.sin(alpha) * HT_diff) / HT_diff) * (position[0] * tropism[0] + position[1] * tropism[1] + position[2] * tropism[2])


    def apply_rules(self, char: str) -> str:
        """This function goes through the rules and applys the new string to return
        """
        newstr: str = ""
        for rule in self.rules:
            for key, value in rule.items():
                if char == key:
                    if "rand" in value:
                        rand_num = random.randrange(0, len(value["rand"]))
                        newstr = value["rand"][rand_num]
                    else:
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