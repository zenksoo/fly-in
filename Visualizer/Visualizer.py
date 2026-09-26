from MLX.libmlx import mlx, mlx_t, mlx_keyfunc, mlx_key_data_t
from MLX.libmlx import (MLX_KEY_E, MLX_KEY_R, MLX_KEY_SPACE,
                        MLX_KEY_LEFT, MLX_KEY_RIGHT)
from PIL import Image
from Simulation import DroneSimulation
from Utils import Drone, Hub, HubType, Connection, Colors
from typing import List, Tuple, Any
from typing import Dict
from .WindowConfig import WindowConfig
from MLXCanvas import MlxCanvas
import random
import ctypes
import os


BANNER_PATH = "./Assets/images/banner.png"

BACKGROUND_LAYER = 0
CONNECTIONS_LAYER = 1
HUBS_LAYER = 4
TEXT_LAYER = 3
DRONE_LAYER = 2
BANNER_LAYER = 5


class MlxVisualizer:
    def __init__(self, config_file: str, simulation: DroneSimulation) -> None:
        self.mlx_ptr: mlx_t
        self.simulation: DroneSimulation = simulation
        self.wcfg: WindowConfig = WindowConfig._from_file(config_file)

    @staticmethod
    def _get_window_resolution(cfg: WindowConfig,
                               hubs: List[Hub]
                               ) -> Tuple[int, int]:
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
        for hub in self.simulation.map_data.hubs.values():
            hub_png: str = "./Assets/images/hub_normal.png"
            if hub.metadata.zone == "priority":
                hub_png = "./Assets/images/hub_priority.png"
            elif hub.metadata.zone == "restricted":
                hub_png = "./Assets/images/hub_restricted.png"
            elif hub.metadata.zone == "blocked":
                hub_png = "./Assets/images/hub_blocked.png"

            png = Image.open(hub_png).convert("RGBA")

            hub.gfx.w, hub.gfx.h = png.size

            shift = self.wcfg.padding_x + hub.gfx.w // 2
            hub.x = shift + hub.x * (80 + self.wcfg.x_gap)

            shift = self.wcfg.padding_y + hub.gfx.h // 2
            hub.y = shift + self.wcfg.y_gap + hub.y * (80 + self.wcfg.y_gap)

            hub.mlx_img = mlx.mlx_new_image(self.mlx_ptr, hub.gfx.w, hub.gfx.h)

            mlx_img_x = hub.x - hub.gfx.w // 2
            mlx_img_y = hub.y - hub.gfx.h // 2

            mlx.mlx_image_to_window(self.mlx_ptr, hub.mlx_img,
                                    mlx_img_x, mlx_img_y)

            hub.mlx_img.contents.instances[0].z = HUBS_LAYER
            MlxCanvas._load_png_to_mlximg(hub.mlx_img,
                                          png, 0, 0,
                                          hub.metadata.color,
                                          Colors.hub_source)

            text_x = hub.x - hub.gfx.w // 2
            text_y = hub.y - hub.gfx.h // 2
            if (hub.type == HubType.start_hub or hub.type == HubType.end_hub):
                hub.metadata.max_drones = self.simulation.map_data.ndrones

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

    def setup_drones(self, hubs: Dict[str, Hub], n_drones: int
                     ) -> Dict[str, Drone]:
        drones: Dict[str, Drone] = {}

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

            drone.mlximg = MlxCanvas._create_layer(self.mlx_ptr,
                                                   coord_x, coord_y,
                                                   coord_z, png_w, png_h)

            drone.position = (start_hub.x, start_hub.y)
            drone.dest_pos = (start_hub.x, start_hub.y)
            drone.dest_hub = start_hub
            drone.color = random.choice(drone_colors)
            MlxCanvas._load_png_to_mlximg(drone.mlximg, drone_png, 0, 0,
                                          drone.color, Colors.blue)
            drones[drone.id] = drone
        start_hub.droneCount = n_drones
        return drones

    def _render_footer(self, texts: List[str]) -> None:
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
            MlxCanvas._draw_text(self.text_layer, txt, x, y,
                                 self.wcfg.font_color)
            x += text_blk

    def add_labeled_box(self, st_x: int, st_y: int, text: str
                        ) -> Dict[str, Tuple[int, int]]:
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

    def _update_hub_capacity_label(self) -> None:
        for hub in self.simulation.map_data.hubs.values():
            hub.droneCount = 0

        for drone in self.simulation.drones.values():
            if drone.dest_hub:
                drone.dest_hub.droneCount += 1

        for hub in self.simulation.map_data.hubs.values():
            new_text = f"0{hub.droneCount}/{hub.metadata.max_drones}"
            if (hub.droneCount > 9):
                new_text = f"{hub.droneCount}/{hub.metadata.max_drones}"

            MlxCanvas._update_text(self.text_layer,
                                   hub.gfx.bottom_label,
                                   new_text)

    @staticmethod
    def update_drone_position(drone: Drone, shift_pos: Tuple[float, float]
                              ) -> None:
        new_pos_x = drone.position[0] + shift_pos[0]
        new_pos_y = drone.position[1] + shift_pos[1]

        drone.mlximg.contents.instances[0].x = round(new_pos_x)
        drone.mlximg.contents.instances[0].y = round(new_pos_y)

    def init_window(self) -> None:
        hubs = list(self.simulation.map_data.hubs.values())

        self.w, self.h = self._get_window_resolution(self.wcfg, hubs)

        self.mlx_ptr = mlx.mlx_init(self.w, self.h,
                                    bytes(self.wcfg.title, "utf-8"),
                                    self.wcfg.resizing)
        self.bg_layer = MlxCanvas._create_layer(self.mlx_ptr, 0, 0,
                                                BACKGROUND_LAYER)
        self.text_layer = MlxCanvas._create_layer(self.mlx_ptr, 0, 0,
                                                  TEXT_LAYER)
        self.connections_layer = MlxCanvas._create_layer(self.mlx_ptr, 0, 0,
                                                         CONNECTIONS_LAYER)
        self.drones_layer = MlxCanvas._create_layer(self.mlx_ptr, 0, 0,
                                                    DRONE_LAYER)

        MlxCanvas._fill_window_bg(self.bg_layer, self.wcfg.bg_color,
                                  self.wcfg.bg_points_effect)

        banner_img = Image.open(BANNER_PATH).convert("RGBA")
        banner_x = (self.w - banner_img.size[0]) // 2
        banner_y = (self.wcfg.padding_y - banner_img.size[1]) // 2

        self.banner = MlxCanvas._create_layer(self.mlx_ptr, banner_x, banner_y,
                                              BANNER_LAYER,
                                              banner_img.size[0],
                                              banner_img.size[1])

        MlxCanvas._load_png_to_mlximg(self.banner, banner_img, 0, 0,
                                      self.wcfg.banner_color,
                                      Colors.white.value)

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
        start_label_x = self.wcfg.padding_x
        start_label_y = self.wcfg.padding_y - 18

        self.turns_label = self.add_labeled_box(start_label_x, start_label_y,
                                                "TURN: 00")

        # add speed label status
        start_label_x += 120

        self.speed_status = self.add_labeled_box(start_label_x, start_label_y,
                                                 "SPEED: 2.0")

        # add width label at to
        start_label_x += 150

        self.add_labeled_box(start_label_x, start_label_y, f"WIDTH: {self.w}")
        start_label_x += 150
        self.add_labeled_box(start_label_x, start_label_y, f"HEIGHT: {self.h}")

    def init_map(self) -> None:

        self.render_hubs()

        self.render_connections(self.simulation.map_data.connections,
                                self.simulation.map_data.hubs)

        self._render_footer([
            "[SPACE] RUN / PAUSE",
            "[R] RESET",
            "[>] SPEED +",
            "[<] SPEED -"
        ])

        self.simulation.drones = self.setup_drones(
            self.simulation.map_data.hubs,
            self.simulation.map_data.ndrones)

    @mlx_keyfunc
    @staticmethod
    def handel_input(key: mlx_key_data_t, param: int) -> None:
        # 1 -> key pressed
        # 0 -> key up
        # 2 -> key down = hover

        if key.action != 0:
            return

        visualizer: MlxVisualizer = ctypes.cast(param, ctypes.py_object).value
        simulation = visualizer.simulation

        if (key.key == MLX_KEY_E):
            os._exit(0)
        elif (key.key == MLX_KEY_R):
            simulation.reset_drones_position()
            simulation.RESET = True
            simulation.RUN_ANIMATION = False
        elif (key.key == MLX_KEY_LEFT):
            if simulation.SPEED > simulation.min_spped:
                simulation.SPEED -= 0.5
                MlxCanvas._update_text(visualizer.text_layer,
                                       visualizer.speed_status,
                                       f"SPEED: {simulation.SPEED}")
        elif (key.key == MLX_KEY_RIGHT):
            if (simulation.SPEED < simulation.max_speed):
                simulation.SPEED += 0.5
                MlxCanvas._update_text(visualizer.text_layer,
                                       visualizer.speed_status,
                                       f"SPEED: {simulation.SPEED}")
        elif (key.key == MLX_KEY_SPACE):
            if not simulation.RUN_ANIMATION:
                simulation.RUN_ANIMATION = True
            else:
                simulation.RUN_ANIMATION = False
