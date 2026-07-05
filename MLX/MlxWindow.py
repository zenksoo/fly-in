from MLX.libmlx import *
import ctypes

class MlxWindow:
    def __init__(self, mlx_ptr: ctypes._Pointer[mlx_t]) -> None:
        self.width = mlx_ptr.contents.width
        self.height = mlx_ptr.contents.height
        self.title = mlx_ptr.contents.title

