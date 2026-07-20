import numpy as np
from MLX.libmlx import *
from PIL import Image
from Utils import pack_rgba, HexColor_to_decimal, Hub, Colors, Connection
from typing import List, Tuple
from Parser import MapParser
import tomllib
from typing import Dict, Any
from .wcfg import WCfg
from .Canvas import Canvas


BANNER_PATH = "./Assets/images/banner.png"

BACKGROUND_LAYER = 0
CONNECTIONS_LAYER = 1
HUBS_LAYER = 2
TEXT_LAYER       = 3
BANNER_LAYER     = 4


class MlxWindow:
    def __init__(self, config_file: str) -> None:
        with open(config_file, "rb") as f:
            data = tomllib.load(f)
        self.wcfg: WCfg = WCfg(**data)
        self.mlx_ptr: mlx_t

    def _create_layer(self, z) -> mlx_image_t:
        img = mlx.mlx_new_image(
            self.mlx_ptr, self.mlx_ptr.contents.width,
            self.mlx_ptr.contents.height
        )
        mlx.mlx_image_to_window(self.mlx_ptr, img, 0, 0)

        img.contents.instances[0].z = z

        return img

    def _add_png_to_window(self, png: str | Image.Image,
                           x: int, y: int, z: int,
                           target_color: str | int | None = None,
                           changed_color: str | int | None = None
                           ) -> mlx_image_t:

        if isinstance(png, str):
            png = Image.open(png).convert("RGBA")

        img_w, img_h = png.size

        mlx_img = mlx.mlx_new_image(self.mlx_ptr, img_w, img_h)
        mlx.mlx_image_to_window(self.mlx_ptr, mlx_img, x, y)


        mlx_img.contents.instances[0].z = z
        Canvas._load_png_to_image(mlx_img, png, changed_color, target_color)

        return mlx_img

    def render_hubs(self, hubs: List[Hub]) -> None:
        self.hubs_layer = self._create_layer(HUBS_LAYER)

        for hub in hubs:
            hub_png: str = "./Assets/images/hub_normal.png"
            if hub.metadata.zone == "priority":
                hub_png = "./Assets/images/hub_priority.png"
            elif hub.metadata.zone == "restricted":
                hub_png = "./Assets/images/hub_restricted.png"
            elif hub.metadata.zone == "blocked":
                hub_png = "./Assets/images/hub_blocked.png"

            hub.x = self.wcfg.padding_x + hub.x * (80 + self.wcfg.x_gap)
            hub.y = self.wcfg.padding_y + hub.y * (80 + self.wcfg.y_gap)

            png = Image.open(hub_png).convert("RGBA")

            hub_color = hub.metadata.color.value
            source_color = 0x8220d3ff
            Canvas._load_png_to_layer(self.hubs_layer,
                                      png, hub.x, hub.y,
                                      hub_color, source_color)

            hub.gfx.w, hub.gfx.h = png.size


            if self.wcfg.enable_hub_name:
                hub.gfx.top_label =  Canvas._draw_text(
                    self.text_layer, hub.name, hub.x, hub.y - 12,
                    self.wcfg.text_color)

            hub.gfx.bottom_label = Canvas._draw_text(
                self.text_layer,
                f"00/{hub.metadata.max_drones}",
                hub.x,
                hub.y + hub.gfx.h + 4,
                self.wcfg.text_color)

    @staticmethod
    def _get_window_resolution(cfg: WCfg, hubs: List[Hub]) -> Tuple[int, int]:
        min_x = min([h.x for h in hubs])
        min_y = min([h.y for h in hubs])

        for h in hubs:
            h.x = abs(h.x) + abs(min_x)
            h.y = abs(h.y) + abs(min_y)

        min_x = min([h.x for h in hubs])
        min_y = min([h.y for h in hubs])

        for h in hubs:
            h.x = abs(h.x) - abs(min_x)
            h.y = abs(h.y) - abs(min_y)

        hubs_x = [h.x for h in hubs]
        hubs_y = [h.y for h in hubs]

        w = (cfg.padding_x * 2) + ((max(hubs_x) + 1) * (80 + cfg.x_gap)) -  cfg.x_gap
        h = (cfg.padding_y * 2) + ((max(hubs_y) + 1) * (80 + cfg.y_gap)) - cfg.y_gap

        if w < 500:
            w = 500

        return (w, h)

    def render_connections(self,
                           connections: List[Connection],
                           hubs: Dict[str, Hub]) -> None:
        self.connections_layer = self._create_layer(CONNECTIONS_LAYER)

        color = 0xFFFFFF62
        for con in connections:
            hub_w = hubs[con.start].gfx.w
            hub_h = hubs[con.start].gfx.h

            sx = int(hubs[con.start].x + (hub_w / 2))
            sy = int(hubs[con.start].y + (hub_h / 2))

            ex = int(hubs[con.end].x + (hub_w / 2))
            ey = int(hubs[con.end].y + (hub_h / 2))

            width = con.metadata.max_link_capacity * 15
            Canvas._draw_line(
                self.connections_layer, sx, sy, ex, ey, width, color)

            if self.wcfg.enable_connection_txt:
                text_x = int((abs(ex - sx) / 2) - 4)
                text_y = int((abs(ey - sy) / 2) - 3)

                text_x += sx if sx < ex else ex
                text_y += sy if sy < ey else ey
                Canvas._draw_text(
                    self.text_layer,
                    f"0{con.metadata.max_link_capacity}",
                    text_x, text_y, self.wcfg.text_color)

    def _window_footer(self, texts: List[str]) -> None:
        x = self.wcfg.padding_x
        y = self.mlx_ptr.contents.height - int(self.wcfg.padding_y / 2)
        txt = f"WIDTH: {self.mlx_ptr.contents.width}"

        total_len = sum([len(txt) for txt in texts])
        space = self.mlx_ptr.contents.width - self.wcfg.padding_x
        space = int((space - total_len) / len(texts))

        block_size = self.mlx_ptr.contents.width
        block_size = int(block_size / len(texts))

        for txt, i in zip(texts, range(len(texts))):
            middle_x = block_size * i + x
            Canvas._draw_text(self.text_layer, txt, middle_x, y)


    def init(self, map: MapParser) -> mlx_t:
        hubs = list(map.hubs.values())

        self.w, self.h = self._get_window_resolution(self.wcfg, hubs)

        self.mlx_ptr = mlx.mlx_init(self.w, self.h, bytes(self.wcfg.title, "utf-8"), True)
        self.bg_layer = self._create_layer(BACKGROUND_LAYER)
        self.text_layer = self._create_layer(TEXT_LAYER)

        Canvas._fill_window_bg(self.bg_layer, self.wcfg.bg_color)

        banner_img = Image.open(BANNER_PATH).convert("RGBA")
        banner_x = (self.w - banner_img.size[0]) // 2
        banner_y = 20
        self._add_png_to_window(banner_img, banner_x, banner_y, BANNER_LAYER)

        self.render_hubs(hubs)

        self.render_connections(map.connections, map.hubs)

        self._window_footer([
            f"WIDTH: {self.mlx_ptr.contents.width}",
            f"HEIGHT: {self.mlx_ptr.contents.height}",
            "SPACE: RUN / PAUSE",
            "STATUS: SOLVED"
        ])

