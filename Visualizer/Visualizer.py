import numpy as np
from MLX.libmlx import *
from PIL import Image
from utils import pack_rgba, HexColor_to_decimal
from typing import Optional


class Canvas:
    @staticmethod
    def fill_image(img: mlx_image_t, pixels_color: str | Image.Image):
        color = 0x00000000
        if not isinstance(pixels_color, Image.Image):
            if isinstance(pixels_color, str):
                # hex color
                if pixels_color.startswith("#"):
                    color = HexColor_to_decimal(pixels_color)
                # image path
                else:
                    pixels_color = Image.open(pixels_color).convert("RGBA")

        for y in range(img.contents.height):
            for x in range(img.contents.width):
                if isinstance(pixels_color, Image.Image):
                    color = pack_rgba(*pixels_color.getpixel((x, y)))
                idx = (y * img.contents.width + x) * 4
                img.contents.pixels[idx] = color >> 24 & 0xFF
                img.contents.pixels[idx + 1] = color >> 16 & 0xFF
                img.contents.pixels[idx + 2] = color >> 8 & 0xFF
                img.contents.pixels[idx + 3] = color & 0xFF


if __name__ == "__main__":
    pass





