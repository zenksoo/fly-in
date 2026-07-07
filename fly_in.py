from MLX.libmlx import *
import ctypes
import tomllib
import numpy as np
from PIL import Image
from typing import Tuple
from Visualizer import Canvas, MlxWindow, WindowCFG


def main():
    with open("./Configs/window.toml", 'rb') as f:
        config = tomllib.load(f)

    wcfg = WindowCFG(**config["window"])
    mlx_window = MlxWindow(wcfg)

    mlx_window.init_window(b"Fly-In")

    mlx.mlx_loop(mlx_window.mlx_ptr)


if __name__ == "__main__":
    main()
