from MLX.libmlx import mlx, mlx_image_t, mlx_t
from PIL import Image
from Utils import Colors
from typing import Dict, Tuple


class MlxCanvas:
    """ A class for creating and managing a canvas in the MLX library. """

    @staticmethod
    def _pack_rgba(r: int, g: int, b: int, a: int) -> int:
        """ Pack RGBA values into a single integer.

        Args:
            r (int): Red component (0-255).
            g (int): Green component (0-255).
            b (int): Blue component (0-255).
            a (int): Alpha component (0-255).

        Returns:
            int: The packed RGBA value as a single integer.
        """

        return (r << 24) | (g << 16) | (b << 8) | a

    @staticmethod
    def _put_pixel(img: mlx_image_t,
                   x: int, y: int,
                   pixel_color: int) -> None:
        """ Put a pixel of a specific color at a given position in an image.

        Args:
            img (mlx_image_t): The image to modify.
            x (int): The x-coordinate of the pixel.
            y (int): The y-coordinate of the pixel.
            pixel_color (int): The color of the pixel in packed RGBA format.
        """

        idx = (y * img.contents.width + x) * 4
        img.contents.pixels[idx] = pixel_color >> 24 & 0xFF
        img.contents.pixels[idx + 1] = pixel_color >> 16 & 0xFF
        img.contents.pixels[idx + 2] = pixel_color >> 8 & 0xFF
        img.contents.pixels[idx + 3] = pixel_color & 0xFF

    @staticmethod
    def _create_layer(mlx_ptr: mlx_t, x: int, y: int,  z: int,
                      width: int | None = None,
                      height: int | None = None) -> mlx_image_t:
        """ Create a new image layer in the MLX library.

        Args:
            mlx_ptr (mlx_t): A pointer to the MLX instance.
            x (int): The x-coordinate of the layer's position.
            y (int): The y-coordinate of the layer's position.
            z (int): The z-index of the layer.
            width (int | None): The width of the layer. If None,
                                use the MLX window width.
            height (int | None): The height of the layer. If None,
                                 use the MLX window height.
        Returns:
            mlx_image_t: The created image layer.
        """
        if not width:
            width = mlx_ptr.contents.width

        if not height:
            height = mlx_ptr.contents.height

        img: mlx_image_t = mlx.mlx_new_image(mlx_ptr,
                                             width, height)

        mlx.mlx_image_to_window(mlx_ptr, img, x, y)

        img.contents.instances[0].z = z

        return img

    @staticmethod
    def _clear_image(mlx_ptr: mlx_t, img: mlx_image_t) -> mlx_image_t:
        """
        Clear an image by deleting it and creating a new one with the same
        dimensions and position.

        Args:
            mlx_ptr (mlx_t): A pointer to the MLX instance.
            img (mlx_image_t): The image to clear.

        Returns:
            mlx_image_t: The cleared image.
        """

        w, h = (img.contents.width, img.contents.height)
        x, y, z = (
            img.contents.instances[0].x,
            img.contents.instances[0].y,
            img.contents.instances[0].z
        )

        mlx.mlx_delete_image(mlx_ptr, img)

        img = mlx.mlx_new_image(mlx_ptr, w, h)
        mlx.mlx_image_to_window(mlx_ptr, img, x, y)

        img.contents.instances[0].z = z

        return img

    @staticmethod
    def _fill_window_bg(img: mlx_image_t, color: int | Colors,
                        bg_point_effect: int | Colors) -> None:
        """
        Fill the entire window with a specific background color, optionally
        adding a point effect.

        Args:
            img (mlx_image_t): The image to fill.
            color (int | Colors): The background color in packed RGBA format or
                                  a Colors enum.
            bg_point_effect (int | Colors): The color for the point effect in
                                            packed RGBA format or a Colors enum
        """

        def _pick_color(color: Colors | int) -> int:
            """ Pick the appropriate color value based on the input type.

            Args:
                color (Colors | int): The color to pick.

            Returns:
                int: The color value in packed RGBA format.
            """

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
                            replacement_color: Colors | int = 0,
                            source_color: Colors | int = 0) -> None:
        """
            Load a PNG image and draw it onto an MLX image layer,
            replacing a specific color if needed.

        Args:
            layer (mlx_image_t): The MLX image layer to draw on.
            png (str | Image.Image): The path to the PNG file
                                     or the Image object.
            x (int): The x-coordinate of the top-left corner of the PNG.
            y (int): The y-coordinate of the top-left corner of the PNG.
            replacement_color (Colors | int): The color to replace in the PNG.
            source_color (Colors | int): The color to replace in the PNG.

        Returns:
            None
        """

        rainbow_colors = [Colors.red, Colors.orange, Colors.yellow,
                          Colors.green,  Colors.blue, Colors.indigo,
                          Colors.violet]
        rainbow_idx = 0
        is_rainbow: bool = False

        if isinstance(png, str):
            png = Image.open(png).convert("RGBA")

        png_w, png_h = png.size

        if isinstance(replacement_color, Colors):
            if replacement_color == Colors.rainbow:
                is_rainbow = True
            replacement_color = replacement_color.value
        if isinstance(source_color, Colors):
            source_color = source_color.value

        for png_y in range(png_h):
            if png_y and png_y % int(png_h / len(rainbow_colors)) == 0:
                rainbow_idx += 1
                if rainbow_idx >= len(rainbow_colors):
                    rainbow_idx = 0
            for png_x in range(png_w):
                color: int = MlxCanvas._pack_rgba(
                    *png.getpixel((png_x, png_y)))  # type: ignore

                if (replacement_color in Colors and source_color and
                   color == source_color):
                    if is_rainbow:
                        color = rainbow_colors[rainbow_idx].value
                    else:
                        color = replacement_color

                MlxCanvas._put_pixel(layer, x + png_x, y + png_y, color)

    @staticmethod
    def _draw_text(layer: mlx_image_t,
                   txt: str, txt_x: int, txt_y: int,
                   color: Colors | int | None = None
                   ) -> Dict[str, Tuple[int, int]]:
        """
        Draw text on an MLX image layer at a specified position with
        a given color.

        Args:
            layer (mlx_image_t): The MLX image layer to draw on.
            txt (str): The text to draw.
            txt_x (int): The x-coordinate of the top-left corner of the text.
            txt_y (int): The y-coordinate of the top-left corner of the text.
            color (Colors | int | None): The color of the text in packed RGBA
                                         format or a Colors enum.
        Returns:
            Dict[str, Tuple[int, int]]: A dictionary containing the start and
                                        end coordinates of the drawn text.
        """

        def draw_char(img: mlx_image_t,
                      char: str, char_idx: int,
                      layer_x: int, layer_y: int,

                      replacement_color: int | None) -> None:
            """ Draw a single character on an MLX image layer at a specified
            position with a given color.

            Args:
                img (mlx_image_t): The MLX image layer to draw on.
                char (str): The character to draw.
                char_idx (int): The index of the character in the text.
                layer_x (int): The x-coordinate of the top-left corner
                               of the character.
                layer_y (int): The y-coordinate of the top-left corner
                               of the character.
                replacement_color (int | None): The color to replace the
                                                character with, if needed.
            """

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
                    pixel_color = MlxCanvas._pack_rgba(
                        *png.getpixel((glyph_x + x, y)))  # type: ignore
                    if (replacement_color and
                       pixel_color == (0xffffff << 8) + 0xff):

                        pixel_color = replacement_color

                    MlxCanvas._put_pixel(img, img_x + x + layer_x,
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
        """
        Delete text from an MLX image layer by clearing the pixels in the
        specified area.

        Args:
            text_layer (mlx_image_t): The MLX image layer to modify.
            start (Tuple[int, int]): The starting coordinates (x, y)
                                    of the area to clear.
            end (Tuple[int, int]): The ending coordinates (x, y)
                                    of the area to clear.
        """

        for y in range(start[1], end[1] + 1):
            for x in range(start[0], end[0] + 1):
                MlxCanvas._put_pixel(text_layer, x, y, 0x00000000)

    @staticmethod
    def _update_text(
            layer: mlx_image_t,
            label_coord: Dict[str, Tuple[int, int]],
            new_content: str) -> None:
        """
        Update the text on an MLX image layer by deleting the old text and
        drawing the new text.

        Args:
            layer (mlx_image_t): The MLX image layer to modify.
            label_coord (Dict[str, Tuple[int, int]]): A dictionary containing
            the start and end coordinates of the old text.
            new_content (str): The new text content to draw.
        """

        MlxCanvas._delete_text(layer, label_coord["start"], label_coord["end"])
        MlxCanvas._draw_text(layer, new_content, label_coord["start"][0],
                             label_coord["start"][1])

    @staticmethod
    def _draw_circle(layer: mlx_image_t,
                     cx: int, cy: int, r: int,
                     pixel_color: int) -> None:
        """
        Draw a filled circle on an MLX image layer at a specified position
        with a given radius and color.

        Args:
            layer (mlx_image_t): The MLX image layer to draw on.
            cx (int): The x-coordinate of the center of the circle.
            cy (int): The y-coordinate of the center of the circle.
            r (int): The radius of the circle.
            pixel_color (int): The color of the circle in packed RGBA format.
        """

        x = 0
        y = -r

        if not r:
            MlxCanvas._put_pixel(layer, cx, cy, pixel_color)
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
        """
        Draw a line on an MLX image layer from (x0, y0) to (x1, y1) with a
        specified thickness and color.

        Args:
            layer (mlx_image_t): The MLX image layer to draw on.
            x0 (int): The x-coordinate of the starting point of the line.
            y0 (int): The y-coordinate of the starting point of the line.
            x1 (int): The x-coordinate of the ending point of the line.
            y1 (int): The y-coordinate of the ending point of the line.
            thickness (int): The thickness of the line.
            pixel_color (int): The color of the line in packed RGBA format.
        """

        sx = x1 - x0
        sy = y1 - y0

        step = max(abs(sx), abs(sy))

        if not step:
            return

        dx = sx / step
        dy = sy / step

        half = thickness // 2
        vx = -dy
        vy = dx

        r = 1
        if not half:
            r = 0

        for i in range(-half, half + 1):
            x = x0 + (vx * i)
            y = y0 + (vy * i)
            for i in range(step):
                MlxCanvas._draw_circle(layer, round(x), round(y),
                                       r, pixel_color)
                x += dx
                y += dy
