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
HUBS_LAYER = 4
TEXT_LAYER = 3
DRONE_LAYER = 2
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
                           target_color: Colors | int | None = None,
                           changed_color: Colors | int | None = None
                           ) -> mlx_image_t:
        print(target_color, changed_color)
        if isinstance(png, str):
            png = Image.open(png).convert("RGBA")

        img_w, img_h = png.size

        mlx_img: mlx_image_t = mlx.mlx_new_image(self.mlx_ptr, img_w, img_h)
        mlx.mlx_image_to_window(self.mlx_ptr, mlx_img, x, y)

        mlx_img.contents.instances[0].z = z
        MlxCanvas._load_png_to_mlximg(mlx_img, png, 0, 0,
                                   target_color, changed_color)

        return mlx_img


    @staticmethod
    def _get_window_resolution(cfg: WindowConfig, hubs: List[Hub]) -> Tuple[int, int]:
        min_x = min([h.x for h in hubs])
        min_y = min([h.y for h in hubs])

        for h in hubs:
            h.x = h.x + abs(min_x)
            h.y = h.y + abs(min_y)

        max_x = max([h.x for h in hubs])
        max_y = max([h.y for h in hubs])

        width = (max_x + 1) * (80 + cfg.x_gap) - cfg.x_gap
        width = (cfg.padding_x * 2) + width

        height = (max_y + 2) * (80 + cfg.y_gap) - cfg.y_gap
        height = (cfg.padding_y * 2) + height

        if width < 500:
            width = 500

        return (width, height)

    def render_hubs(self) -> None:
        for hub_name in self.map_data.hubs.keys():

            hub = self.map_data.hubs[hub_name]
            print(hub.name, hub.x, hub.y)
            hub_png: str = "./Assets/images/hub_normal.png"
            if hub.metadata.zone == "priority":
                hub_png = "./Assets/images/hub_priority.png"
            elif hub.metadata.zone == "restricted":
                hub_png = "./Assets/images/hub_restricted.png"
            elif hub.metadata.zone == "blocked":
                hub_png = "./Assets/images/hub_blocked.png"


            png = Image.open(hub_png).convert("RGBA")

            hub.gfx.w, hub.gfx.h = png.size

            hub.x = self.wcfg.padding_x + hub.gfx.w // 2 + hub.x * (80 + self.wcfg.x_gap)
            hub.y = self.wcfg.padding_y + hub.gfx.h // 2 + self.wcfg.y_gap + hub.y * (80 + self.wcfg.y_gap)

            hub.mlx_img = mlx.mlx_new_image(self.mlx_ptr, hub.gfx.w, hub.gfx.h)

            mlx_img_x = hub.x - hub.gfx.w // 2
            mlx_img_y = hub.y - hub.gfx.h // 2

            mlx.mlx_image_to_window(self.mlx_ptr, hub.mlx_img,
                                    mlx_img_x, mlx_img_y)

            hub.mlx_img.contents.instances[0].z = HUBS_LAYER

            MlxCanvas._load_png_to_mlximg(hub.mlx_img,
                                       png, 0, 0,
                                       hub.metadata.color, Colors.hub_source)

            text_x = hub.x - hub.gfx.w // 2
            text_y = hub.y - hub.gfx.h // 2
            if (hub.type == HubType.start_hub or hub.type == HubType.end_hub):
                hub.metadata.max_drones = self.map_data.ndrones

            hub.gfx.top_label = MlxCanvas._draw_text(
                self.text_layer, hub.name, text_x, text_y - 12,
                self.wcfg.font_color)

            hub.gfx.bottom_label = MlxCanvas._draw_text(
                self.text_layer,
                f"00/{hub.metadata.max_drones}",
                text_x,
                text_y + hub.gfx.h + 4,
                self.wcfg.font_color)

    def render_connections(self,
                           connections: List[Connection],
                           hubs: Dict[str, Hub]) -> None:
        color = 0xC0C0C0AE
        for con in connections:
            hub_w = hubs[con.start].gfx.w
            hub_h = hubs[con.start].gfx.h

            sx = hubs[con.start].x
            sy = hubs[con.start].y

            ex = hubs[con.end].x
            ey = hubs[con.end].y

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

        drone_colors = [Colors.blue, Colors.red, Colors.yellow,
                        Colors.pink, Colors.black, Colors.cyan,
                        Colors.green, Colors.gray, Colors.azure, Colors.lime]

        for i in range(1, n_drones + 1):
            drone: Drone = Drone(f"D{i}")

            coord_x = start_hub.x - png_w // 2
            coord_y = start_hub.y - png_h // 2
            coord_z = HUBS_LAYER + i + 1

            drone.mlximg = MlxCanvas._create_layer(self.mlx_ptr, coord_x, coord_y, coord_z, png_w, png_h)


            drone.position = (start_hub.x, start_hub.y)
            drone.distination = start_hub
            drone.color = random.choice(drone_colors)
            MlxCanvas._load_png_to_mlximg(drone.mlximg, drone_png, 0, 0,
                                          drone.color, Colors.blue)
            self.drones[drone.id] = drone
        start_hub.droneCount = n_drones

    def _reset_drones_position(self) -> None:
        start_hub = [
            hub for hub in self.map_data.hubs.values() if hub.type == HubType.start_hub
            ][0]

        png_w = list(self.drones.values())[0].mlximg.contents.width
        png_h = list(self.drones.values())[0].mlximg.contents.height

        x = start_hub.x - png_w // 2
        y = start_hub.y - png_h // 2

        for drone in self.drones.values():
            if drone.arrived:
                drone.distination.droneCount -= 1
            drone.position = (x, y)
            drone.mlximg.contents.instances[0].x = x + round(5 * random.random())
            drone.mlximg.contents.instances[0].y = y + round(5 * random.random())
            drone.distination = start_hub

        start_hub.droneCount = len(self.drones.values())


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
            MlxCanvas._draw_text(self.text_layer, txt, x, y, self.wcfg.font_color)
            x += text_blk

    def _add_boxed_label(self, st_x: int, st_y: int, text: str) -> Dict[str, Tuple[int, int]]:
        end_x = st_x + 6 * len(text) + 32
        end_y = st_y + 18

        MlxCanvas._draw_line(self.text_layer, st_x, st_y, end_x, st_y,
                          0, self.wcfg.font_color)

        MlxCanvas._draw_line(self.text_layer, st_x, st_y, st_x, end_y,
                          0, self.wcfg.font_color)
        MlxCanvas._draw_line(self.text_layer, end_x, st_y, end_x, end_y,
                          0, self.wcfg.font_color)

        MlxCanvas._draw_line(self.text_layer, st_x, end_y, end_x, end_y,
                          0, self.wcfg.font_color)

        return MlxCanvas._draw_text(self.text_layer, text, st_x + 16, st_y + 6,
                                 self.wcfg.font_color)

    def init_window(self) -> None:
        hubs = list(self.map_data.hubs.values())

        self.w, self.h = self._get_window_resolution(self.wcfg, hubs)

        self.mlx_ptr = mlx.mlx_init(self.w, self.h,
                                    bytes(self.wcfg.title, "utf-8"),
                                    self.wcfg.resizing)
        self.bg_layer = MlxCanvas._create_layer(self.mlx_ptr, 0, 0, BACKGROUND_LAYER)
        self.text_layer = MlxCanvas._create_layer(self.mlx_ptr,0, 0, TEXT_LAYER)
        self.connections_layer = MlxCanvas._create_layer(self.mlx_ptr, 0, 0, CONNECTIONS_LAYER)
        self.drones_layer = MlxCanvas._create_layer(self.mlx_ptr, 0, 0, DRONE_LAYER)

        MlxCanvas._fill_window_bg(self.bg_layer, self.wcfg.bg_color,
                               self.wcfg.bg_points_effect)

        banner_img = Image.open(BANNER_PATH).convert("RGBA")
        banner_x = (self.w - banner_img.size[0]) // 2
        banner_y = (self.wcfg.padding_y - banner_img.size[1]) // 2

        self._add_png_to_window(banner_img, banner_x, banner_y, BANNER_LAYER,
                                self.wcfg.banner_color, Colors.white.value)

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

        # add turns label
        ndrone_label_st_x = self.wcfg.padding_x
        ndrone_label_st_y = self.wcfg.padding_y - 18

        self.turns_label = self._add_boxed_label(ndrone_label_st_x, ndrone_label_st_y, "TURN: 00")

        # add speed label status
        speed_label_st_x = self.wcfg.padding_x + 100
        speed_label_st_y = self.wcfg.padding_y - 18

        self.speed_status = self._add_boxed_label(speed_label_st_x, speed_label_st_y, "SPEED: 1.0")

    def init_map(self) -> None:

        self.render_hubs()

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

            if drone.distination != hub and drone.distination.droneCount > 0:
                drone.distination.droneCount -= 1
                drone.distination = hub
                drone.arrived = False

                moved_drones.append(drone)

        return moved_drones

    def _update_hub_capacity_label(self) -> None:
        for hub in self.map_data.hubs.values():
            new_text = f"0{hub.droneCount}/{hub.metadata.max_drones}"
            if (hub.droneCount > 9):
                new_text = f"{hub.droneCount}/{hub.metadata.max_drones}"

            MlxCanvas._change_label_content(self.text_layer,
                                            hub.gfx.bottom_label,
                                            new_text)

    def _move_toward(self, drone: Drone, SPEED: float = 1.0, show_path: bool = False) -> None:

        if drone._has_arrived():
            return

        direction = drone._get_vector_direction_to()

        img_w, img_h = (drone.mlximg.contents.width, drone.mlximg.contents.height)

        new_pos_x = drone.position[0] + direction[0] * SPEED * (random.random() * 4)
        new_pos_y = drone.position[1] + direction[1] * SPEED * (random.random() * 4)

        if show_path:
            MlxCanvas._draw_line(self.drones_layer,
                                 round(drone.position[0]),
                                 round(drone.position[1]),
                                 round(new_pos_x),
                                 round(new_pos_y),
                                 0, drone.color.value)

        drone.position = (new_pos_x, new_pos_y)

        drone.mlximg.contents.instances[0].x = round(drone.position[0]) - img_w // 2
        drone.mlximg.contents.instances[0].y = round(drone.position[1]) - img_h // 2






