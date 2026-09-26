from MLX.libmlx import mlx_loop_hook_func, mlx_image_t
from MLXCanvas import MlxCanvas
import ctypes
from typing import List, Tuple, Dict
from Utils import Drone, HubType
from random import random
from Parser import MapParser
import time


class DroneSimulation:
    max_speed = 4.0
    min_spped = 1.0

    def __init__(self, map_data: MapParser | str) -> None:
        if isinstance(map_data, str):
            map_data = MapParser.from_file(map_data)

        self.bigest_dest: int = 0

        self.map_data = map_data
        self.drones: Dict[str, Drone] = {}

        self.solution: List[List[str]]
        self.routes: List[str] = []
        self.turn: int = 0

        self.SPEED: float = 2.0
        self.RESET: bool = False

        self.READY_TO_MOVE_DRONES: List[Drone] = []
        self.TURNS_FINISHED: bool = False

        self.RUN_ANIMATION: bool = False

    def _calculate_bigest_dest(self) -> None:
        self.bigest_dest = 0
        for drone in self.READY_TO_MOVE_DRONES:
            sx = drone.dest_pos[0] - drone.position[0]
            sy = drone.dest_pos[1] - drone.position[1]

            if (max(abs(sx), abs(sy)) > self.bigest_dest):
                self.bigest_dest = int(max(abs(sx), abs(sy)))

    def _update_moved_drones(self) -> None:
        moved_drones: List[Drone] = []

        self.routes = self.solution[self.turn]

        for st in self.routes:
            route = st.split("-")
            drone = self.drones[route[0]]
            curr_pos = drone.position
            new_pos: Tuple[int, int] = (0, 0)
            new_hub = None
            if (len(route) == 3):
                start_hub = self.map_data.hubs[route[1]]
                end_hub = self.map_data.hubs[route[2]]

                x = (start_hub.x + end_hub.x) // 2
                y = (start_hub.y + end_hub.y) // 2

                new_pos = (x, y)
            else:
                dest_hub = self.map_data.hubs[route[1]]
                new_pos = (dest_hub.x, dest_hub.y)
                new_hub = dest_hub

            if new_pos != curr_pos:
                drone.dest_pos = new_pos
                drone.dest_hub = new_hub

                moved_drones.append(drone)

        self.READY_TO_MOVE_DRONES = moved_drones
        self._calculate_bigest_dest()

    @staticmethod
    def _get_vector_direction_to(drone: Drone,
                                 step: int) -> Tuple[float, float]:

        sx = drone.dest_pos[0] - drone.position[0]
        sy = drone.dest_pos[1] - drone.position[1]

        # step = max(abs(sx), abs(sy))

        dx = sx / step
        dy = sy / step

        return (dx, dy)

    @staticmethod
    def _drone_arrived(drone: Drone) -> bool:
        x, y = (drone.position[0], drone.position[1])

        if ((x >= drone.dest_pos[0] - 5 and x <= drone.dest_pos[0] + 5) and
           (y >= drone.dest_pos[1] - 5 and y <= drone.dest_pos[1] + 5)):
            return True
        return False

    def reset_drones_position(self) -> None:
        from Visualizer import MlxVisualizer
        drones = list(self.drones.values())
        hubs = list(self.map_data.hubs.values())
        start_hub = [
            hub for hub in hubs
            if hub.type == HubType.start_hub
            ][0]

        png_w = drones[0].mlximg.contents.width
        png_h = drones[0].mlximg.contents.height

        x = start_hub.x - png_w // 2
        y = start_hub.y - png_h // 2

        for drone in drones:
            drone.position = (x, y)
            MlxVisualizer.update_drone_position(
                drone,
                (round(5 * random()), round(5 * random())))
            drone.dest_pos = (start_hub.x, start_hub.y)
            drone.dest_hub = start_hub

    def _move_toward(self, drone: Drone,
                     path_layer: mlx_image_t,
                     show_path: bool = False) -> None:
        from Visualizer import MlxVisualizer

        if self._drone_arrived(drone):
            return

        dir = self._get_vector_direction_to(drone, self.bigest_dest)
        img_w = drone.mlximg.contents.width
        img_h = drone.mlximg.contents.height

        new_pos_x = drone.position[0] + dir[0] * self.SPEED * (random() * 4)
        new_pos_y = drone.position[1] + dir[1] * self.SPEED * (random() * 4)

        if show_path:
            MlxCanvas._draw_line(path_layer,
                                 round(drone.position[0]),
                                 round(drone.position[1]),
                                 round(new_pos_x),
                                 round(new_pos_y),
                                 0, drone.color.value)

        drone.position = (new_pos_x, new_pos_y)

        MlxVisualizer.update_drone_position(drone,
                                            (-img_w // 2, -img_h // 2))

    @mlx_loop_hook_func
    @staticmethod
    def movement_animation(param: int) -> None:
        from Visualizer import MlxVisualizer
        visualizer: MlxVisualizer = ctypes.cast(param, ctypes.py_object).value
        simulation: DroneSimulation = visualizer.simulation

        if simulation.RESET:
            simulation.RESET = False
            simulation.TURNS_FINISHED = False
            simulation.turn = 0
            visualizer._update_hub_capacity_label()
            simulation._update_moved_drones()
            MlxCanvas._update_text(visualizer.text_layer,
                                   visualizer.turns_label, "TURN: 00")
            visualizer.drones_layer = MlxCanvas._clear_image(
                visualizer.mlx_ptr,
                visualizer.drones_layer)

        if not simulation.RUN_ANIMATION or simulation.TURNS_FINISHED:
            return

        for drone in simulation.READY_TO_MOVE_DRONES:
            simulation._move_toward(drone, visualizer.drones_layer,
                                    visualizer.wcfg.enable_drones_path)

        if all([simulation._drone_arrived(d)
                for d in simulation.READY_TO_MOVE_DRONES]):
            simulation.turn += 1
            if simulation.turn < len(simulation.solution):
                simulation._update_moved_drones()
            if (simulation.turn > 9):
                new_content = f"TURN: {simulation.turn}"
            else:
                new_content = f"TURN: 0{simulation.turn}"
            MlxCanvas._update_text(visualizer.text_layer,
                                   visualizer.turns_label, new_content)
            visualizer._update_hub_capacity_label()
            time.sleep(0.3)
        if simulation.turn >= len(simulation.solution):
            simulation.TURNS_FINISHED = True
