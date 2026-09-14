from MLX import mlx, mlx_t, mlx_image_t
from PIL import Image
from Utils import Drone, Hub, HubType, Connection, Colors
from typing import List, Tuple, Any
from Parser import MapParser
import tomllib
from typing import Dict
from .wcfg import WCfg
from .Canvas import Canvas
import math
from random import randint

BANNER_PATH = "./Assets/images/banner.png"

BACKGROUND_LAYER = 0
CONNECTIONS_LAYER = 1
HUBS_LAYER = 2
TEXT_LAYER = 3
DRONE_LAYER = 4
BANNER_LAYER = 5



class MlxWindow:
    def __init__(self, config_file: str) -> None:
        with open(config_file, "rb") as f:
            data = tomllib.load(f)
        self.wcfg: WCfg = WCfg(**data["window"])
        self.mlx_ptr: mlx_t

    def _create_layer(self, z: int, width: int | None = None,
                      height: int | None = None) -> mlx_image_t:

        if not width:
            width = self.mlx_ptr.contents.width

        if not height:
            height = self.mlx_ptr.contents.height

        img: mlx_image_t = mlx.mlx_new_image(
            self.mlx_ptr, width, height)
        mlx.mlx_image_to_window(self.mlx_ptr, img, 0, 0)

        img.contents.instances[0].z = z

        return img

    def _add_png_to_window(self, png: str | Image.Image,
                           x: int, y: int, z: int,
                           target_color: Colors | None = None,
                           changed_color: Colors | None = None
                           ) -> mlx_image_t:

        if isinstance(png, str):
            png = Image.open(png).convert("RGBA")

        img_w, img_h = png.size

        mlx_img: mlx_image_t = mlx.mlx_new_image(self.mlx_ptr, img_w, img_h)
        mlx.mlx_image_to_window(self.mlx_ptr, mlx_img, x, y)

        mlx_img.contents.instances[0].z = z
        Canvas._load_png_to_mlximg(mlx_img, png, 0, 0, changed_color, target_color)

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

            Canvas._load_png_to_mlximg(self.hubs_layer,
                                      png, hub.x, hub.y,
                                      hub.metadata.color, Colors.hub_source)

            hub.gfx.w, hub.gfx.h = png.size

            if self.wcfg.enable_hub_name:
                hub.gfx.top_label = Canvas._draw_text(
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

        max_x = max([h.x for h in hubs])
        max_y = max([h.y for h in hubs])

        width = (max_x + 1) * (80 + cfg.x_gap) - cfg.x_gap
        width = (cfg.padding_x * 2) + width

        height = (max_y + 1) * (80 + cfg.y_gap) - cfg.y_gap
        height = (cfg.padding_y * 2) + height

        if width < 500:
            width = 500

        return (width, height)

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

            width = con.metadata.max_link_capacity
            width *= (16 - (2 * con.metadata.max_link_capacity))
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

        total_blk = len(texts)
        break_footer:bool = False

        window_width = self.mlx_ptr.contents.width
        valid_width = window_width - (self.wcfg.padding_x * 2)



        text_blk = max([len(txt) * 6 for txt in texts])

        total_min_spaces = (total_blk + 1) * 20

        if text_blk * total_blk + total_min_spaces > valid_width:
            break_footer = True

        def calculate_spacing(row: int) -> Any:
            sp = valid_width - (text_blk * row)
            return int(sp / (row + 1))

        row_items = total_blk

        if break_footer:
            row_items = (int(total_blk / 2)
                         if not total_blk % 2 else
                         int(total_blk / 2) + 1)
        else:
            y += 20

        spacing = calculate_spacing(row_items)

        for txt, i in zip(texts, range(total_blk)):
            if (break_footer and i == row_items):
                spacing = calculate_spacing(int(total_blk / 2))
                y += 32
                x = self.wcfg.padding_x
            x += spacing
            Canvas._draw_text(self.text_layer, txt, x, y)
            x += text_blk

    def _init_nturns_label(self) -> Dict[str, Tuple[int, int]]:
        st_x = self.wcfg.padding_x - 40
        end_x = self.wcfg.padding_x + 80
        st_y = self.wcfg.padding_y - 72
        end_y = self.wcfg.padding_y - 40

        Canvas._draw_line(self.text_layer, st_x, st_y, end_x, st_y, 2, 0xA2A2A2FF)
        Canvas._draw_line(self.text_layer, st_x, st_y, st_x, end_y, 2, 0xA2A2A2FF)
        Canvas._draw_line(self.text_layer, end_x, st_y, end_x, end_y, 2, 0xA2A2A2FF)

        text = "TURN: 00"

        return Canvas._draw_text(self.text_layer, text, st_x + 32, st_y + 15, Colors.white)

    # def _calculate_drone_position_in_hub(
    #         self, hub: Hub, idx: int) -> Tuple[int, int]:

    #     return (0, 0)



    def init(self, map: MapParser) -> None:
        hubs = list(map.hubs.values())

        self.w, self.h = self._get_window_resolution(self.wcfg, hubs)
        print(self.w, self.h)

        self.mlx_ptr = mlx.mlx_init(self.w, self.h,
                                    bytes(self.wcfg.title, "utf-8"),
                                    self.wcfg.resizing)
        self.bg_layer = self._create_layer(BACKGROUND_LAYER)
        self.text_layer = self._create_layer(TEXT_LAYER)

        Canvas._fill_window_bg(self.bg_layer, self.wcfg.bg_color,
                               self.wcfg.bg_points_effect)

        banner_img = Image.open(BANNER_PATH).convert("RGBA")
        banner_x = (self.w - banner_img.size[0]) // 2
        banner_y = 25
        self._add_png_to_window(banner_img, banner_x, banner_y, BANNER_LAYER)

        self.turns_label = self._init_nturns_label()
        # Canvas._change_label_content(self.text_layer, self.turns_label, "TURN: 9999")

# need fix to be simple it's looks good in the design that's why i add them :)
        Canvas._draw_line(self.bg_layer, self.wcfg.padding_x - 40, self.wcfg.padding_y - 40, self.w - self.wcfg.padding_x + 40, self.wcfg.padding_y - 40, 1, 0xA2A2A2A6)
        Canvas._draw_line(self.bg_layer, self.wcfg.padding_x - 40, self.h - self.wcfg.padding_y + 40, self.w - self.wcfg.padding_x + 40, self. h - self.wcfg.padding_y + 40, 1, 0xA2A2A2A6)

        self.render_hubs(hubs)

        self.render_connections(map.connections, map.hubs)

        self._window_footer([
            f"WIDTH: {self.mlx_ptr.contents.width}",
            f"HEIGHT: {self.mlx_ptr.contents.height}",
            "SPACE: RUN / PAUSE",
            "|>: SPEED UP",
            "<|: SLOWER"
        ])

        # setup drones
        self.drones: Dict[str, Drone] = {}
        start_hub = [hub for hub in map.hubs.values() if hub.type == HubType.start_hub][0]
        drone_colors = [
            Colors.red, Colors.purple, Colors.yellow, Colors.blue,
            Colors.green, Colors.pink, Colors.brown
        ]
        drone_png = Image.open("./Assets/images/Drone.png").convert("RGBA")
        DImgWidth, DimgHeight = drone_png.size

        print(hubs[0].gfx.w)

        # calculate the position of each drone on hub
        # we have hub width and height so the total column is width / DImgWidth
        # and total rows is height / DImgHeight
        # and i will put extra drone that his position is out the hub on each other in last position
        nColumns = int(hubs[0].gfx.w / DImgWidth)
        nRows = int(hubs[0].gfx.h / DimgHeight)

        fullRows = math.ceil(map.ndrones / nColumns)
        if fullRows > nRows:
            fullRows = nRows
        fullColumns = nColumns if map.ndrones > nColumns else map.ndrones

        st_y = int((hubs[0].gfx.h - (DimgHeight * fullRows)) / 2)
        st_x = int((hubs[0].gfx.w - (DImgWidth * fullColumns)) / 2)

        xidx = 0
        yidx = 0

        for i in range(map.ndrones):
            drone = Drone(f"D{i + 1}")
            if i >= len(drone_colors):
                drone_color = drone_colors[randint(0, len(drone_colors) - 1)]
            else: drone_color = drone_colors[i]

            drone.cord = (start_hub.x + st_x + DImgWidth * xidx,
                          start_hub.y + st_y + DimgHeight * yidx)
            drone.mlximg = self._add_png_to_window(drone_png, drone.cord[0],
                drone.cord[1], DRONE_LAYER + i, Colors.blue, drone_color)

            self.drones[drone.id] = drone


            if xidx == nColumns - 1 and i + 1 < nRows * nColumns:
                xidx = 0
                yidx += 1
            elif i + 1 < nRows * nColumns:
                xidx += 1




    def engine(self, map: MapParser, solution: List[List[str]]) ->None:
        pass
