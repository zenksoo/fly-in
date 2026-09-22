from MLX.libmlx import mlx, mlx_t, mlx_image_t, mlx_loop_hook_func
from PIL import Image
from Utils import Drone, Hub, HubType, Connection, Colors
from typing import List, Tuple, Any
from Parser import MapParser
import tomllib
from typing import Dict
from .wcfg import WindowConfig
from .Canvas import MlxCanvas
import random
import ctypes
import time
from datetime import datetime

BANNER_PATH = "./Assets/images/banner.png"

BACKGROUND_LAYER = 0
CONNECTIONS_LAYER = 1
HUBS_LAYER = 2
TEXT_LAYER = 3
DRONE_LAYER = 4
BANNER_LAYER = 5


class MlxVisualizer:
    def __init__(self, config_file: str, map_data: MapParser) -> None:
        self.mlx_ptr: mlx_t

        self.wcfg: WindowConfig = WindowConfig._from_file(config_file)
        self.solution : List[List[str]] = []
        self.map_data = map_data
        self.run_animation = False

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
        MlxCanvas._load_png_to_mlximg(mlx_img, png, 0, 0,
                                   changed_color, target_color)

        return mlx_img


    @staticmethod
    def _get_window_resolution(cfg: WindowConfig, hubs: List[Hub]) -> Tuple[int, int]:
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

        height = (max_y + 2) * (80 + cfg.y_gap) - cfg.y_gap
        height = (cfg.padding_y * 2) + height

        if width < 500:
            width = 500

        return (width, height)

    def render_hubs(self, hubs: Dict[str, Hub]) -> None:
        for hub in hubs.values():
            hub_png: str = "./Assets/images/hub_normal.png"
            if hub.metadata.zone == "priority":
                hub_png = "./Assets/images/hub_priority.png"
            elif hub.metadata.zone == "restricted":
                hub_png = "./Assets/images/hub_restricted.png"
            elif hub.metadata.zone == "blocked":
                hub_png = "./Assets/images/hub_blocked.png"

            hub.x = self.wcfg.padding_x + hub.x * (80 + self.wcfg.x_gap)
            hub.y = self.wcfg.padding_y + self.wcfg.y_gap + hub.y * (80 + self.wcfg.y_gap)

            png = Image.open(hub_png).convert("RGBA")

            hub.gfx.w, hub.gfx.h = png.size

            hub.mlx_img = mlx.mlx_new_image(self.mlx_ptr, hub.gfx.w, hub.gfx.h)

            mlx.mlx_image_to_window(self.mlx_ptr, hub.mlx_img, hub.x, hub.y)
            hub.mlx_img.contents.instances[0].z = HUBS_LAYER

            MlxCanvas._load_png_to_mlximg(hub.mlx_img,
                                       png, 0, 0,
                                       hub.metadata.color, Colors.hub_source)


            if self.wcfg.enable_hub_name:
                hub.gfx.top_label = MlxCanvas._draw_text(
                    self.text_layer, hub.name, hub.x, hub.y - 12,
                    self.wcfg.font_color)

            hub.gfx.bottom_label = MlxCanvas._draw_text(
                self.text_layer,
                f"00/{hub.metadata.max_drones}",
                hub.x,
                hub.y + hub.gfx.h + 4,
                self.wcfg.font_color)

    def render_connections(self,
                           connections: List[Connection],
                           hubs: Dict[str, Hub]) -> None:
        color = 0xC0C0C0AE
        for con in connections:
            hub_w = hubs[con.start].gfx.w
            hub_h = hubs[con.start].gfx.h

            sx = int(hubs[con.start].x + (hub_w / 2))
            sy = int(hubs[con.start].y + (hub_h / 2))

            ex = int(hubs[con.end].x + (hub_w / 2))
            ey = int(hubs[con.end].y + (hub_h / 2))

            width = con.metadata.max_link_capacity
            width *= (16 - (2 * con.metadata.max_link_capacity))
            MlxCanvas._draw_line(
                self.connections_layer, sx, sy, ex, ey, width, color)

            if self.wcfg.enable_connection_txt:
                text_x = int((abs(ex - sx) / 2) - 4)
                text_y = int((abs(ey - sy) / 2) - 3)

                text_x += sx if sx < ex else ex
                text_y += sy if sy < ey else ey
                MlxCanvas._draw_text(
                    self.text_layer,
                    f"0{con.metadata.max_link_capacity}",
                    text_x, text_y, self.wcfg.font_color)

    def setup_drones(self, hubs: Dict[str, Hub], n_drones: int) -> None:
        self.drones: Dict[str, Drone] = {}



        start_hub = [
            hub for hub in hubs.values() if hub.type == HubType.start_hub
            ][0]

        drone_png = Image.open("./Assets/images/Drone.png").convert("RGBA")
        png_w, png_h = drone_png.size

        hub_area = list(hubs.values())[0].mlx_img.contents.width
        randomize_position = 0

        # init_drone_coordinate = [hubs.values()[0]]

        x = start_hub.x + (hub_area - png_w) // 2
        y = start_hub.y + (hub_area - png_h) // 2

        drone_colors = [Colors.blue, Colors.red, Colors.yellow,
                        Colors.pink, Colors.black, Colors.cyan,
                        Colors.green, Colors.gray, Colors.azure, Colors.lime]

        for i in range(1, n_drones + 1):

            drone: Drone = Drone(f"D{i}")
            coord_x = x + random.randint(-randomize_position, randomize_position)
            coord_y = y + random.randint(-randomize_position, randomize_position)
            coord_z = DRONE_LAYER + i - 1
            drone.mlximg = mlx.mlx_new_image(self.mlx_ptr, png_w, png_h)

            mlx.mlx_image_to_window(self.mlx_ptr, drone.mlximg, coord_x, coord_y)

            MlxCanvas._load_png_to_mlximg(drone.mlximg, drone_png, 0, 0,
                                          random.choice(drone_colors), Colors.blue)

            drone.mlximg.contents.instances[0].z = coord_z
            drone.position = (x, y)
            self.drones[drone.id] = drone

    def _reset_drones_position(self) -> None:
        start_hub = [
            hub for hub in self.map_data.hubs.values() if hub.type == HubType.start_hub
            ][0]

        png_w = list(self.drones.values())[0].mlximg.contents.width
        png_h = list(self.drones.values())[0].mlximg.contents.height

        hub_w = list(self.map_data.hubs.values())[0].mlx_img.contents.width
        hub_h = list(self.map_data.hubs.values())[0].mlx_img.contents.height

        x = start_hub.x + (hub_w - png_w) // 2
        y = start_hub.y + (hub_h - png_h) // 2

        for drone in self.drones.values():
            drone.position = (x, y)
            drone.mlximg.contents.instances[0].x = x
            drone.mlximg.contents.instances[0].y = y



    def _window_footer(self, texts: List[str]) -> None:
        x = self.wcfg.padding_x
        y = self.mlx_ptr.contents.height - int(self.wcfg.padding_y / 2)

        lines_gap = 32

        total_blk = len(texts)
        break_footer: bool = False

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
            # >> 8 is the height of character (px unit)
            y = y - (8 * 2 + lines_gap) // 2
            row_items = (int(total_blk / 2)
                         if not total_blk % 2 else
                         int(total_blk / 2) + 1)

        spacing = calculate_spacing(row_items)

        for txt, i in zip(texts, range(total_blk)):
            if (break_footer and i == row_items):
                spacing = calculate_spacing(int(total_blk / 2))
                y += lines_gap
                x = self.wcfg.padding_x
            x += spacing
            MlxCanvas._draw_text(self.text_layer, txt, x, y)
            x += text_blk

    def _init_nturns_label(self) -> Dict[str, Tuple[int, int]]:
        st_x = self.wcfg.padding_x
        end_x = self.wcfg.padding_x + 100
        st_y = self.wcfg.padding_y - 40
        end_y = self.wcfg.padding_y

        MlxCanvas._draw_line(self.text_layer, st_x, st_y, end_x, st_y,
                          1, 0xA2A2A2FF)

        MlxCanvas._draw_line(self.text_layer, st_x, st_y, st_x, end_y,
                          1, 0xA2A2A2FF)
        MlxCanvas._draw_line(self.text_layer, end_x, st_y, end_x, end_y,
                          1, 0xA2A2A2FF)

        MlxCanvas._draw_line(self.text_layer, st_x, end_y, end_x, end_y,
                          1, 0xA2A2A2FF)

        text = "TURN: 00"

        return MlxCanvas._draw_text(self.text_layer, text, st_x + 25, st_y + 15,
                                 Colors.white)

    def init_window(self) -> None:
        hubs = list(self.map_data.hubs.values())

        self.w, self.h = self._get_window_resolution(self.wcfg, hubs)

        self.mlx_ptr = mlx.mlx_init(self.w, self.h,
                                    bytes(self.wcfg.title, "utf-8"),
                                    self.wcfg.resizing)
        self.bg_layer = MlxCanvas._create_layer(self.mlx_ptr, BACKGROUND_LAYER)
        self.text_layer = MlxCanvas._create_layer(self.mlx_ptr, TEXT_LAYER)
        self.connections_layer = MlxCanvas._create_layer(self.mlx_ptr, CONNECTIONS_LAYER)

        MlxCanvas._fill_window_bg(self.bg_layer, self.wcfg.bg_color,
                               self.wcfg.bg_points_effect)

        banner_img = Image.open(BANNER_PATH).convert("RGBA")
        banner_x = (self.w - banner_img.size[0]) // 2
        banner_y = (self.wcfg.padding_y - banner_img.size[1]) // 2

        self._add_png_to_window(banner_img, banner_x, banner_y, BANNER_LAYER)

        # draw line under the padding_y at the top and above them in the bottom
        st_x = self.wcfg.padding_x
        st_y = self.wcfg.padding_y
        end_x = self.w - self.wcfg.padding_x

        MlxCanvas._draw_line(self.bg_layer,
                             st_x, st_y,
                             end_x, st_y, 0, 0xA2A2A2A6)

        st_y = self.h - self.wcfg.padding_y

        MlxCanvas._draw_line(self.bg_layer,
                             st_x, st_y,
                             end_x, st_y, 0, 0xA2A2A2A6)



        self.turns_label = self._init_nturns_label()


    def init_map(self) -> None:

        self.render_hubs(self.map_data.hubs)

        self.render_connections(self.map_data.connections,
                                self.map_data.hubs)


        self._window_footer([
            f"WIDTH: {self.mlx_ptr.contents.width}",
            f"HEIGHT: {self.mlx_ptr.contents.height}",
            "SPACE: RUN / PAUSE",
            "|>: SPEED UP",
            "<|: SLOWER"
        ])

        self.setup_drones(self.map_data.hubs, self.map_data.ndrones)

    def _get_moved_drones(self, turn: int) -> List[Drone]:
        moved_drones: List[Drone] = []

        turn_solution = self.solution[turn]

        for st in turn_solution:
            drone_id, hub_name = st.split("-")
            drone = self.drones[drone_id]
            hub = self.map_data.hubs[hub_name]

            hub_w, hub_h = (hub.mlx_img.contents.width,
                            hub.mlx_img.contents.height)


            distination_x = hub.x + (hub_w - drone.mlximg.contents.width) // 2
            distination_y = hub.y + (hub_h - drone.mlximg.contents.height) // 2

            drone.distination = (distination_x, distination_y)

            moved_drones.append(drone)

        return moved_drones





    # def run(self, turn: List[str]) -> bool:
    #     for frame in turn:
    #         drone_name, hub_name = frame.split("-")
    #         drone = self.drones[drone_name]
    #         hub = self.map_data.hubs[hub_name]
    #         sx = hub.x - drone.position[0]
    #         sy = hub.y - drone.position[1]

    #         step = max(abs(sx), abs(sy))

    #         dx = sx / step
    #         dy = sy / step
    #         old_time = time.time()
    #         x = drone.mlximg.contents.instances[0].x
    #         y = drone.mlximg.contents.instances[0].y


    #         for i in range(step):
    #             current_time = time.time()
    #             dt = 0.001

    #             drone.mlximg.contents.instances[0].x = round(x)
    #             drone.mlximg.contents.instances[0].y = round(y)

    #             x += dx * dt
    #             y += dy * dt

    #     return True

    # @mlx_loop_hook_func
    # @staticmethod
    # def engine(param) -> None:
    #     speed = 10
    #     window: MlxVisualizer = ctypes.cast(param, ctypes.py_object).value
    #     for sol in window.solution:
    #         for fram in sol:
    #             drone_name, hub_name = fram.split("-")
    #             drone = window.drones[drone_name]
    #             hub = window.map_data.hubs[hub_name]

    #             sx = hub.x - drone.position[0]
    #             sy = hub.y - drone.position[1]

    #             print(sx, sy)

    #             step = max(abs(sx), abs(sy))

    #             dx = sx / step
    #             dy = sy / step
    #             old_time = datetime.now()
    #             x = drone.position[0]
    #             y = drone.position[1]


    #             for i in range(step):
    #                 current_time = datetime.now()
    #                 dt = current_time - old_time
    #                 dt = 0.1


    #                 print(i * dt)
    #                 drone.mlximg.contents.instances[0].x = round(x)
    #                 drone.mlximg.contents.instances[0].y = round(y)

    #                 x += dx * dt
    #                 y += dy * dt





