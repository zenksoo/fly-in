from MLX.libmlx import mlx, mlx_image_t, mlx_t
from PIL import Image
from Utils import pack_rgba, Colors
# from CExceptions import CanvasError
from typing import Dict, Tuple
import math


class MlxCanvas:
    @staticmethod
    def _put_pixel(img: mlx_image_t,
                    x: int, y: int,
                    pixel_color: int) -> None:
        idx = (y * img.contents.width + x) * 4
        img.contents.pixels[idx] = pixel_color >> 24 & 0xFF
        img.contents.pixels[idx + 1] = pixel_color >> 16 & 0xFF
        img.contents.pixels[idx + 2] = pixel_color >> 8 & 0xFF
        img.contents.pixels[idx + 3] = pixel_color & 0xFF

    @staticmethod
    def _create_layer(mlx_ptr: mlx_t, z: int, width: int | None = None,
                    height: int | None = None) -> mlx_image_t:
        if not width:
            width = mlx_ptr.contents.width

        if not height:
            height = mlx_ptr.contents.height

        img: mlx_image_t = mlx.mlx_new_image(mlx_ptr,
                                             width, height)

        mlx.mlx_image_to_window(mlx_ptr, img, 0, 0)

        img.contents.instances[0].z = z

        return img

    @staticmethod
    def _fill_window_bg(img: mlx_image_t, color: int | Colors,
                        bg_point_effect: int | Colors) -> None:

        def _pick_color(color: Colors | int) -> int:
            if isinstance(color, Colors):
                return color.value
            else:
                return color

        decimal_pxcolor: int = _pick_color(color)

        for y in range(img.contents.height):
            for x in range(img.contents.width):

                if (x - 4) % 32 == 0 and (y - 4) % 32 == 0:
                    decimal_pxcolor = _pick_color(bg_point_effect)
                else:
                    decimal_pxcolor = _pick_color(color)
                MlxCanvas._put_pixel(img, x, y, decimal_pxcolor)

    @staticmethod
    def _load_png_to_mlximg(layer: mlx_image_t,
                            png: str | Image.Image, x: int, y: int,
                            replacement_color: Colors | None = None,
                            source_color: Colors | None = None) -> None:

        rainbow_colors = [Colors.red, Colors.orange, Colors.yellow,
                          Colors.green,  Colors.blue, Colors.indigo,
                          Colors.violet]
        rainbow_idx = 0

        if isinstance(png, str):
            png = Image.open(png).convert("RGBA")

        png_w, png_h = png.size

        for png_y in range(png_h):
            if png_y and png_y % int(png_h / len(rainbow_colors)) == 0:
                rainbow_idx += 1
                if rainbow_idx >= len(rainbow_colors):
                    rainbow_idx = 0
            for png_x in range(png_w):
                color = pack_rgba(*png.getpixel((png_x, png_y)))

                if (replacement_color and source_color and
                   color == source_color.value):
                    if replacement_color == Colors.rainbow:
                        color = rainbow_colors[rainbow_idx].value
                    else:
                        color = replacement_color.value

                MlxCanvas._put_pixel(layer, x + png_x, y + png_y, color)

    @staticmethod
    def _draw_text(layer: mlx_image_t,
                   txt: str, txt_x: int, txt_y: int,
                   color: Colors | int | None = None
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
            else:
                char = '.'
                png = Image.open("./Assets/fonts/digits.png")
                glyph_x = DIGITS.index(char)

            glyph_x = glyph_x * 6
            img_x = char_idx * 6

            for y in range(8):
                for x in range(6):
                    pixel_color = pack_rgba(*png.getpixel((glyph_x + x, y)))
                    if (replacement_color and
                       pixel_color == (0xffffff << 8) + 0xff):

                        pixel_color = replacement_color

                    MlxCanvas._put_pixel(img, img_x +  x + layer_x,
                                       y + layer_y, pixel_color)

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
                MlxCanvas._put_pixel(text_layer, x, y, 0x00000000)


    @staticmethod
    def _draw_circle(layer: mlx_image_t, cx: int, cy: int, r: int, pixel_color: int) -> None:
        x = 0
        y = -r

        if not r:
            MlxCanvas._put_pixel(layer,cx, cy, pixel_color)
            return

        while (x < -y):
            midp = y + 0.5
            c = midp*midp + x*x

            if c > r*r:
                y += 1

            MlxCanvas._put_pixel(layer, cx + x, cy + y, pixel_color)
            MlxCanvas._put_pixel(layer, cx + x, cy - y, pixel_color)
            MlxCanvas._put_pixel(layer, cx - x, cy + y, pixel_color)
            MlxCanvas._put_pixel(layer, cx - x, cy - y, pixel_color)

            MlxCanvas._put_pixel(layer, cx + y, cy + x, pixel_color)
            MlxCanvas._put_pixel(layer, cx - y, cy - x, pixel_color)
            MlxCanvas._put_pixel(layer, cx - y, cy + x, pixel_color)
            MlxCanvas._put_pixel(layer, cx + y, cy - x, pixel_color)


            for i in range(cx - x, cx + x + 1):
                MlxCanvas._put_pixel(layer, i, cy + y, pixel_color)
                MlxCanvas._put_pixel(layer, i, cy - y, pixel_color)

            for i in range(cx + y, cx - y):
                MlxCanvas._put_pixel(layer, i, cy + x, pixel_color)
                MlxCanvas._put_pixel(layer, i, cy - x, pixel_color)

            x += 1


    @staticmethod
    def _draw_line(layer: mlx_image_t, x0: int, y0: int,
                   x1: int, y1: int, thickness: int,
                   pixel_color: int) -> None:

        sx = x1 - x0
        sy = y1 - y0

        step = max(abs(sx), abs(sy))

        if not step: return

        dx = sx / step
        dy = sy / step

        half = thickness // 2
        vx = -dy
        vy = dx

        for i in range(-half, half + 1):
            x = round(x0 + (vx * i))
            y = round(y0 + (vy * i))
            for i in range(step):
                MlxCanvas._draw_circle(layer, round(x), round(y), 1, pixel_color)
                x += dx
                y += dy

    @staticmethod
    def _change_label_content(
            layer: mlx_image_t,
            label_coord: Dict[str, Tuple[int, int]],
            new_content: str) -> None:

        MlxCanvas._delete_text(layer, label_coord["start"], label_coord["end"])
        MlxCanvas._draw_text(layer, new_content, label_coord["start"][0],
                          label_coord["start"][1])
