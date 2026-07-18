import numpy as np
from MLX.libmlx import *
from PIL import Image
from Utils import Hub
from typing import List, Tuple
from Parser import MapParser
import tomllib
from typing import Dict, Any
from .wcfg import Cfg
from .Canvas import Canvas


class MlxWindow:
    def __init__(self, config_file: str) -> None:
        with open(config_file, "rb") as f:
            data = tomllib.load(f)
        self.wcfg: Cfg = Cfg(**data)
        self.mlx_ptr: mlx_t

    def init(self, map: MapParser) -> mlx_t:
        self.w, self.h = self._get_window_resolution(self.wcfg,
            list(map.hubs.values()))

        self.mlx_ptr = mlx.mlx_init(self.w, self.h, bytes(self.wcfg.window.title, "utf-8"), False)
        self.bg_img = mlx.mlx_new_image(self.mlx_ptr, self.w, self.h)

        mlx.mlx_image_to_window(self.mlx_ptr, self.bg_img, 0, 0)

        Canvas._fill_image_by_static_color(self.bg_img, self.wcfg.window.bg_color)

        self.bg_img.contents.instances[0].z = 1

        banner_x = int(self.w / 2) - int(180 / 2)
        banner_y = 40

        hubs = list(map.hubs.values())
        self._add_img_to_window("./Assets/images/banner.png", 180, 60, banner_x, banner_y, 3, None)
        for h in hubs:
            drone_png: str
            if h.metadata.zone == "priority":
                drone_png = "./Assets/images/hub_priority.png"
            elif h.metadata.zone == "restricted":
                drone_png = "./Assets/images/hub_restricted.png"
            elif h.metadata.zone == "blocked":
                drone_png = "./Assets/images/hub_blocked.png"
            else:
                drone_png = "./Assets/images/hub_normal.png"
            h.x = self.wcfg.sizing.padding_x + (h.x * (80 + self.wcfg.sizing.space))
            h.y = self.wcfg.sizing.padding_y + (h.y * (80 + self.wcfg.sizing.space))
            print(h.x, h.y)

            self._add_img_to_window(drone_png, 80, 80, h.x, h.y, 2, h.metadata.color.value)

        self._add_img_to_window("./Assets/images/Drone.png", 32, 32, 80, 80, 3, None)

    @staticmethod
    def _get_window_resolution(cfg: Cfg, hubs: List[Hub]) -> Tuple[int, int]:
        min_x = min([h.x for h in hubs])
        min_y = min([h.y for h in hubs])

        print(min_x)
        print(min_y)

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

        print(hubs_x)
        print(hubs_y)

        w = (cfg.sizing.padding_x * 2) + ((max(hubs_x) + 1) * (80 + cfg.sizing.space)) -  cfg.sizing.space
        h = (cfg.sizing.padding_y * 2) + ((max(hubs_y) + 1) * (80 + cfg.sizing.space)) - cfg.sizing.space

        if w < 500:
            w = 500

        return (w, h)

    def _add_img_to_window(self, png: str,
            width: int, height: int, x: int, y: int, z: int,
            color: int | None) -> mlx_image_t:

        img = mlx.mlx_new_image(self.mlx_ptr, width, height)
        img_bg = Image.open(png).convert("RGBA")
        print(img_bg)

        mlx.mlx_image_to_window(self.mlx_ptr, img, x, y)
        Canvas._fill_image_by_png(
            img, img_bg, color, True)
        img.contents.instances[0].z = z

        return img
