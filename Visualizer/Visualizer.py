import numpy as np
from MLX.libmlx import *
from PIL import Image
from utils import pack_rgba, HexColor_to_decimal
from typing import Optional
from pydantic import BaseModel, model_validator, Field, ValidationError


# class Drone:
#     def __init__(self, drone_name: str) -> None:
#         self.name = drone_name
#         self.img: mlx_image_t = mlx.mlx_new_image()

class WindowCFG(BaseModel):
    WINDOW_BG_COLOR: str
    WINDOW_WIDTH: int
    WINDOW_HEIGHT: int


class Canvas:
    @staticmethod
    def _fill_image_by_static_color(img: mlx_image_t, color: str | int) -> None:
        pixel_color: int = 0
        if isinstance(color, str):
            pixel_color = HexColor_to_decimal(color)
        else:
            pixel_color = color

        for y in range(img.contents.height):
            for x in range(img.contents.width):

                idx = (y * img.contents.width + x) * 4
                img.contents.pixels[idx] = pixel_color >> 24 & 0xFF
                img.contents.pixels[idx + 1] = pixel_color >> 16 & 0xFF
                img.contents.pixels[idx + 2] = pixel_color >> 8 & 0xFF
                img.contents.pixels[idx + 3] = pixel_color & 0xFF

    @staticmethod
    def _fill_image_by_png(img: mlx_image_t,
                          png: str | Image.Image,
                          changed_color: str | int | None = None,
                          change_color: bool = False) -> None:
        if isinstance(png, str):
            png = Image.open(png).convert("RGBA")

        if change_color and isinstance(changed_color, str):
            changed_color = HexColor_to_decimal(changed_color)

        for y in range(img.contents.height):
            for x in range(img.contents.width):
                color = pack_rgba(*png.getpixel((x, y)))
                if change_color and color == pack_rgba(130, 32, 211, 255):
                    color = changed_color

                idx = (y * img.contents.width + x) * 4
                img.contents.pixels[idx] = color >> 24 & 0xFF
                img.contents.pixels[idx + 1] = color >> 16 & 0xFF
                img.contents.pixels[idx + 2] = color >> 8 & 0xFF
                img.contents.pixels[idx + 3] = color & 0xFF

class MlxWindow:
    wcfg: WindowCFG
    width: int
    height: int
    mlx_ptr: mlx_t
    bg_img: mlx_image_t

    def __init__(self, window_cfg: WindowCFG) -> None:
        MlxWindow.wcfg = window_cfg
        MlxWindow.width = window_cfg.WINDOW_WIDTH
        MlxWindow.height = window_cfg.WINDOW_HEIGHT

    @staticmethod
    def _fill_window_bg(bg_color: str) -> None:
        Canvas._fill_image_by_static_color(MlxWindow.bg_img, bg_color)

    def init_window(self, title: bytes) -> None:
        MlxWindow.mlx_ptr = mlx.mlx_init(self.width, self.height, title, False)
        MlxWindow.bg_img = mlx.mlx_new_image(self.mlx_ptr, self.width, self.height)

        self._fill_window_bg(MlxWindow.wcfg.WINDOW_BG_COLOR)
        mlx.mlx_image_to_window(self.mlx_ptr, self.bg_img, 0, 0)
        self.bg_img.contents.instances[0].z = 0

    def _put_in_middle(self, img: mlx_image_t) -> None:
        x = int((self.width / 2) - (img.contents.width / 2))
        y = int((self.height / 2) - (img.contents.height / 2))

        mlx.mlx_image_to_window(self.mlx_ptr, img, x, y)


    def _put_in_topleft(self, img: mlx_image_t) -> None:
        pass


    def middle_window(self):
        img = mlx.mlx_new_image(self.mlx_ptr, 180, 240)
        Canvas._fill_image_by_png(img, "./Assets/menu.png")

        self._put_in_middle(img)



class Drone:
    def __init__(self) -> None:
        self.color = 0xff0000
