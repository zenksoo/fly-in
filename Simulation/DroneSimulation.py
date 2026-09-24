from MLX.libmlx import mlx_loop_hook_func, mlx_image_t
from Visualizer import MlxVisualizer
from MLXCanvas import MlxCanvas
import ctypes
from typing import List, Tuple, Dict
from Utils import Drone, HubType
from random import random
from Parser import MapParser

class DroneSimulation:
    def __init__(self, map_data: MapParser | str) -> None:
        if isinstance(map_data, str):
            map_data = MapParser.from_file(map_data)

        self.map_data = map_data
        self.drones: Dict[str, Drone] = {}

        self.solution: List[List[str]]
        self.routes: List[str] = []
        self.turn: int = 0


        self.SPEED: float = 1.0
        self.RESET: bool = False

        self.READY_TO_MOVE_DRONES: List[Drone] = []
        self.READY_TO_MOVE_ARRIVED: bool = False

        self.RUN_ANIMATION: bool = False

    def _update_moved_drones(self) -> None:
        moved_drones: List[Drone] = []

        self.routes = self.solution[self.turn]

        for st in self.routes:
            drone_id, hub_name = st.split("-")
            drone = self.drones[drone_id]
            hub = self.map_data.hubs[hub_name]

            if drone.distination != hub and drone.distination.droneCount > 0:
                drone.distination.droneCount -= 1
                drone.distination = hub
                drone.arrived = False

                moved_drones.append(drone)


        self.READY_TO_MOVE_DRONES = moved_drones

    @staticmethod
    def _get_vector_direction_to(drone: Drone) -> Tuple[float, float]:

        sx = drone.distination.x - drone.position[0]
        sy = drone.distination.y - drone.position[1]

        step = max(abs(sx), abs(sy))

        dx = sx / step
        dy = sy / step

        return (dx, dy)

    @staticmethod
    def _has_arrived(drone: Drone) -> bool:
        x, y = (drone.position[0], drone.position[1])

        if ((x >= drone.distination.x - 5 and x <= drone.distination.x + 5) and
            (y >= drone.distination.y - 5 and y <= drone.distination.y + 5)):
            if not drone.arrived:
                drone.distination.droneCount += 1
                drone.arrived = True
            return True
        return False

    def reset_drones_position(self) -> None:
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
            if drone.arrived:
                drone.distination.droneCount -= 1
            drone.position = (x, y)
            MlxVisualizer.update_drone_position(drone,
                                                (round(5 * random()), round(5 * random())))
            drone.distination = start_hub

        start_hub.droneCount = len(drones)

    def _move_toward(self, drone: Drone,
                      path_layer: mlx_image_t ,
                      show_path: bool = False) -> None:

        if self._has_arrived(drone):
            return

        direction = self._get_vector_direction_to(drone)
        img_w = drone.mlximg.contents.width
        img_h = drone.mlximg.contents.height

        new_pos_x = drone.position[0] + direction[0] * self.SPEED * (random() * 4)
        new_pos_y = drone.position[1] + direction[1] * self.SPEED * (random() * 4)

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
        visualizer: MlxVisualizer = ctypes.cast(param, ctypes.py_object).value
        simulation = visualizer.simulation

        if simulation.RESET:
            simulation.RESET = False
            simulation.READY_TO_MOVE_ARRIVED = False
            simulation.turn = 0
            visualizer._update_hub_capacity_label()

            simulation._update_moved_drones()
            MlxCanvas._update_text(visualizer.text_layer, visualizer.turns_label, "TURN: 00")
            visualizer.drones_layer = MlxCanvas._clear_image(visualizer.mlx_ptr, visualizer.drones_layer)

        if not simulation.RUN_ANIMATION or simulation.READY_TO_MOVE_ARRIVED : return

        if simulation.RUN_ANIMATION:
            visualizer._update_hub_capacity_label()
            # for drone in simulation.READY_TO_MOVE_DRONES:
            #     print(drone.id, drone.distination.name)
            for drone in simulation.READY_TO_MOVE_DRONES:
                simulation._move_toward(drone, visualizer.drones_layer, visualizer.wcfg.enable_drones_path)

            if all([d.arrived for d in simulation.READY_TO_MOVE_DRONES]):
                simulation.turn += 1
                if simulation.turn < len(simulation.solution):
                    simulation._update_moved_drones()
                if (simulation.turn > 9):
                    new_content = f"TURN: {simulation.turn}"
                else:
                    new_content = f"TURN: 0{simulation.turn}"
                MlxCanvas._update_text(visualizer.text_layer, visualizer.turns_label, new_content)
            if simulation.turn >= len(simulation.solution):
                simulation.READY_TO_MOVE_ARRIVED = True



