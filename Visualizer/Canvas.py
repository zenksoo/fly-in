from MLX.libmlx import *
from PIL import Image
from Utils import HexColor_to_decimal, pack_rgba


class Canvas:
    @staticmethod
    def _fill_image_by_static_color(img: mlx_image_t, color: str | int) -> None:
        decimal_pxcolor: int = 0
        if isinstance(color, str):
            decimal_pxcolor = HexColor_to_decimal(color)
        else:
            decimal_pxcolor = color

        for y in range(img.contents.height):
            for x in range(img.contents.width):

                idx = (y * img.contents.width + x) * 4
                img.contents.pixels[idx] = decimal_pxcolor >> 24 & 0xFF
                img.contents.pixels[idx + 1] = decimal_pxcolor >> 16 & 0xFF
                img.contents.pixels[idx + 2] = decimal_pxcolor >> 8 & 0xFF
                img.contents.pixels[idx + 3] = decimal_pxcolor & 0xFF

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
                if changed_color and change_color and color == pack_rgba(130, 32, 211, 255):
                    color = changed_color

                idx = (y * img.contents.width + x) * 4
                img.contents.pixels[idx] = color >> 24 & 0xFF
                img.contents.pixels[idx + 1] = color >> 16 & 0xFF
                img.contents.pixels[idx + 2] = color >> 8 & 0xFF
                img.contents.pixels[idx + 3] = color & 0xFF

