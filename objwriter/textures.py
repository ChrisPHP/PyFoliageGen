from seaborn import color_palette
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import random
import numpy as np

class Textures:
    def get_palette_colours(self) -> tuple:
        palettes = ["rocket", "mako", "flare", "crest", "viridis", "plasma", "inferno", "magma", "cividis"]

        rand_pal = random.randrange(0, len(palettes))
        chosen_pal = color_palette(palettes[rand_pal])
        rand_col = random.randrange(0, len(chosen_pal))

        return chosen_pal[rand_col]
    

    def create_lighter_gradient(self, start_rgb: tuple, steps: int):
        brightness = np.linalg.norm(start_rgb)

        color_gradient = [tuple(min(value + i, 1.0) for value in start_rgb) for i in np.linspace(0, 1 - brightness, steps)]

        return color_gradient