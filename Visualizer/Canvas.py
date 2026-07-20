from MLX.libmlx import *
from PIL import Image
from Utils import HexColor_to_decimal, pack_rgba, Colors
from CExceptions import *
from typing import List, Dict, Tuple


class Canvas:
    @staticmethod
    def _fill_pixel(img: mlx_image_t,
                    x: int, y: int,
                    pixel_color: int) -> None:
        idx = (y * img.contents.width + x) * 4
        img.contents.pixels[idx] = pixel_color >> 24 & 0xFF
        img.contents.pixels[idx + 1] = pixel_color >> 16 & 0xFF
        img.contents.pixels[idx + 2] = pixel_color >> 8 & 0xFF
        img.contents.pixels[idx + 3] = pixel_color & 0xFF

    @staticmethod
    def _fill_window_bg(img: mlx_image_t, color: int | Colors) -> None:

        def _pick_color(color: Colors | int) -> int:
            if isinstance(color, Colors):
                return color.value
            else:
                return color

        decimal_pxcolor = _pick_color(color)

        for y in range(img.contents.height):
            for x in range(img.contents.width):

                if (x - 4) % 32 == 0 and (y - 4) % 32 == 0:
                    decimal_pxcolor = HexColor_to_decimal("#919191ff")
                else:
                    decimal_pxcolor = _pick_color(color)
                Canvas._fill_pixel(img, x, y, decimal_pxcolor)

    @staticmethod
    def _load_png_to_image(img: mlx_image_t,
                          png: str | Image.Image,
                          replacement_color: str | int | None = None,
                          source_color: str | int | None = None) -> None:
        if isinstance(png, str):
            png = Image.open(png).convert("RGBA")

        if isinstance(replacement_color, str):
            try:
                replacement_color = HexColor_to_decimal(replacement_color)
            except Exception:
                raise CanvasError(
                    f"invalid value to HexColor_to_decimal method\n\
                    \n\tvalue must be a valid hex color format as string (e.g #00ff00).")

        if isinstance(source_color, str):
            try:
                source_color = HexColor_to_decimal(source_color)
            except Exception:
                raise CanvasError(
                    f"invalid value to HexColor_to_decimal method\n\
                    \n\tvalue must be a valid hex color format as string (e.g #00ff00).")

        for y in range(img.contents.height):
            for x in range(img.contents.width):
                pixel_color = pack_rgba(*png.getpixel((x, y)))
                if replacement_color and source_color and pixel_color == source_color:
                    pixel_color = replacement_color

                Canvas._fill_pixel(img, x, y, pixel_color)

    @staticmethod
    def _load_png_to_layer(layer: mlx_image_t,
        png: str | Image.Image, x: int, y: int,
        replacement_color: str | int | None = None,
        source_color: int | None = None) -> None:

        if isinstance(png, str):
            png = Image.open(png).convert("RGBA")

        png_w, png_h = png.size

        if isinstance(replacement_color, str):
            replacement_color = HexColor_to_decimal(replacement_color)

        for png_y in range(png_h):
            for png_x in range(png_w):
                color = pack_rgba(*png.getpixel((png_x, png_y)))

                if replacement_color and color == source_color:
                    color = replacement_color

                Canvas._fill_pixel(layer, x + png_x, y + png_y, color)

    @staticmethod
    def _draw_text(layer: mlx_image_t,
                   txt: str, txt_x: int, txt_y: int,
                   color: int | None = None
                   ) -> Dict[str, Tuple[int, int]]:

        def draw_char(img: mlx_image_t,
                      char: str, char_idx: int,
                      layer_x: int, layer_y: int,
                      replacement_color: int | None) -> None:
            LOWERCASE = "abcdefghijklmnopqrstuvwxyz"
            UPPERCASE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            DIGITS = "1234567890!\"#%'()~+-/[]<>:.,_| "

            png: Image.Image
            glyph_x: int = 0
            if char in LOWERCASE:
                png = Image.open("./Assets/fonts/lowercase.png")
                glyph_x = LOWERCASE.index(char)
            elif char in UPPERCASE:
                png = Image.open("./Assets/fonts/uppercase.png")
                glyph_x = UPPERCASE.index(char)
            elif char in DIGITS:
                png = Image.open("./Assets/fonts/digits.png")
                glyph_x = DIGITS.index(char)

            glyph_x = glyph_x * 6;
            img_x = char_idx * 6

            for y in range(8):
                for x in range(6):
                    pixel_color = pack_rgba(*png.getpixel((glyph_x + x, y)))
                    if replacement_color and pixel_color == (0xffffff << 8) + 0xff:
                        pixel_color = replacement_color
                    Canvas._fill_pixel(img, img_x + x + layer_x, y + layer_y, pixel_color)

        if isinstance(color, Colors):
            color = color.value

        for idx, char in enumerate(txt):
            draw_char(layer, char, idx, txt_x, txt_y, color)

        return {
            "start": (txt_x, txt_y),
            "end": (txt_x + (len(txt) * 6), txt_y + 8)
        }

    @staticmethod
    def _delete_text(text_layer: mlx_image_t,
                     start: Tuple[int, int],
                     end: Tuple[int, int]
                     ) -> None:

        for y in range(start[1], end[1] + 1):
            for x in range(start[0], end[0] + 1):
                Canvas._fill_pixel(text_layer, x, y, 0x00000000)

    @staticmethod
    def _draw_line(img: mlx_image_t, x0, y0, x1, y1, width,
                   color: int):
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        # Calculate perpendicular offsets for thickness
        # length provides normalization for the width scaling
        import math
        length = math.sqrt(dx*dx + dy*dy)
        if length == 0:
            return

        # Standard integer scaling for thickness offsets
        # x_offset and y_offset define the thickness direction
        # We multiply by (width - 1) / 2 to center the line
        w_factor = (width - 1) / (2.0 * length)
        x_offset = int(dy * w_factor)
        y_offset = int(dx * w_factor)

        while True:
            # Instead of drawing one pixel, draw a perpendicular span
            # to create the desired width
            for w in range(-int(width/2), int((width+1)/2)):
                # Offset the pixel perpendicular to the line direction
                px = x0 + (w * (1 if dy > dx else 0) * (-sy if sx > 0 else sy))
                py = y0 + (w * (1 if dx >= dy else 0) * (sx if sy > 0 else -sx))
                Canvas._fill_pixel(img, px, py, color)

            if x0 == x1 and y0 == y1:
                break

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
