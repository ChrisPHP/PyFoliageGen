from seaborn import color_palette
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import random
import numpy as np

class Textures:
    def get_palette_colours(self):
        uniform_palettes = ["rocket", "mako", "flare", "crest", "viridis", "plasma", "inferno", "magma", "cividis"]
        sequential_palettes = [
            "Greys", "Reds", "Greens", "Blues", "Oranges", "Purples", "BuGn",
            "BuPu", "GnBu", "OrRd", "PuBu", "RdPu", "YlGn", "PuBuGn", "YlGn",
            "PuBuGn", "YlGnBu", "YlGnBu", "YlOrBr", "YlOrRd"
        ]

        rand_pal = random.randrange(0, len(sequential_palettes))
        chosen_pal = color_palette(sequential_palettes[rand_pal])
        rand_col = random.randrange(0, len(chosen_pal))

        #self.create_lighter_gradient(start_rgb=chosen_pal[rand_col], steps=10, max_lightness=0.3)

        return chosen_pal


    def create_lighter_gradient(self, start_rgb: tuple, steps: int, max_lightness: float=1.0):
        brightness = np.linalg.norm(start_rgb)

        color_gradient = [
            tuple(max(min(value + i, max_lightness), 0.0) for value in start_rgb)
            for i in np.linspace(0, max_lightness - brightness, steps)
        ]
        return color_gradient