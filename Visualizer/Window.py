from MLX.libmlx import *
from typing import List

class Window:
    def __init__(self, mlx_ptr) -> None:
        self.drone_images: List = []
        pass


    pass


class Drone:
    def __init__(self, mlx_ptr, color) -> None:
        self.mlx_img = mlx.mlx_new_image(mlx_ptr, 32, 32)
        pass
