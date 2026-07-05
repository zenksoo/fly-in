from MLX.libmlx import *
import ctypes
import tomllib
import numpy as np
from PIL import Image
from typing import Tuple
from Visualizer import Canvas, MlxWindow, WindowCFG


WINDOW: mlx_image_t
WINDOW_W: int = 1240
WINDOW_H: int = 767




# def unpack_rgba(color: int) -> Tuple[int, int, int ,int]:
#     return (color >> 24, color >> 16 & 0xFF, color >> 8 & 0xFF, color & 0xFF)



# # @staticmethod
# # def _fill_image(img, color: int = 0xffffffff) -> None:
# #     for i in range(image.content.height)
# def window_background() -> None:
#     global window_w
#     global window_h
#     bg_color = "#5C6062"
#     window_w = mlx_ptr.contents.width
#     window_h = mlx_ptr.contents.height
#     image = mlx.mlx_new_image(mlx_ptr, window_w, window_h)

#     canvas.fill_image(image, bg_color)
#     mlx.mlx_image_to_window(mlx_ptr, image, 0, 0)
#     image.contents.instances[0].z = 0


# def fill_pixel(img, x, y, color: int):
#     idx = (y * img.contents.width + x) * 4
#     img.contents.pixels[idx] = color >> 24 & 0xFF
#     img.contents.pixels[idx + 1] = color >> 16 & 0xFF
#     img.contents.pixels[idx + 2] = color >> 8 & 0xFF
#     img.contents.pixels[idx + 3] = color & 0xFF

# class ColorPicker:
#     def __init__(self, color_path: str) -> None:
#         with open(color_path, "rb") as f:
#             self.colors = tomllib.load(f)
#         print(self.colors)
#         self.colors["map_design"]["bg"]


# @mlx_loop_hook_func
# def decimal_color_val(param):
#     pixel_image = Image.open("./Assets/Drone.png").convert("RGBA")
#     hex_color = "#828282"

#     canvas.fill_image(image, pixel_image)


# def ft_fill_colors(image: ctypes._Pointer[mlx_image_t], color: int) -> None:
#     for x in range(image.contents.width):
#         for y in range(image.contents.height):
#             mlx.mlx_put_pixel(image, x, y, color)


# @mlx_loop_hook_func
# def events_hook(param):
#     if mlx.mlx_is_key_down(mlx_ptr, MLX_KEY_A):
#         mlx.mlx_delete_image(mlx_ptr, image)
#         image.contents.enabled = True if image.contents.enabled == False else False
#     pass


# @mlx_loop_hook_func
# def resize_window(param):
#     if mlx_ptr.contents.width != window_w:
#         print(window_w, window_h)
#         window_background()
#         print("the window is resizing ?? ")
#     pass


if __name__ == "__main__":


    with open("config.toml", "rb") as f:
        config = tomllib.load(f)

    wcfg = WindowCFG(**config["window"])
    mlx_window = MlxWindow(wcfg)

    mlx_window.init_window(b"Fly-in")

    mlx_window.middle_window()

    img = mlx.mlx_new_image(mlx_window.mlx_ptr, 80, 80)
    Canvas._fill_image_by_png(img, "./Assets/hub.png", "#D80000", True)
    # Canvas.fill_image(img, "./Assets/hub.png")
    mlx.mlx_image_to_window(mlx_window.mlx_ptr, img, 0, 0)
    img.contents.instances[0].z = 2

    mlx.mlx_loop(mlx_window.mlx_ptr)



    # global mlx_ptr
    # global image
    # global canvas
    # global window_w
    # global window_h

    # canvas = Canvas()


    # mlx_ptr = mlx.mlx_init(1240, 767, b"Fly-In", True)

    # window_w = mlx_ptr.contents.width
    # window_h = mlx_ptr.contents.height

    # window_background()

    # image: mlx_image_t = mlx.mlx_new_image(mlx_ptr, 32, 32)

    # mlx.mlx_image_to_window(mlx_ptr, image, 0, 0)
    # image.contents.instances[0].z = 2
    # mlx.mlx_loop_hook(mlx_ptr, decimal_color_val, ctypes.cast(mlx_ptr, c_void_p))
    # mlx.mlx_loop_hook(mlx_ptr, events_hook, ctypes.cast(mlx_ptr, c_void_p))
    # mlx.mlx_loop_hook(mlx_ptr, resize_window, ctypes.cast(mlx_ptr, c_void_p))


