from MLX.libmlx import mlx, mlx_t, mlx_loop_hook_func, c_void_p
from MLX.libmlx import MLX_KEY_E, MLX_KEY_R, MLX_KEY_RIGHT, MLX_KEY_LEFT, MLX_KEY_SPACE
import argparse
from Visualizer import MlxVisualizer, WindowConfig
from Parser import MapParser
from CExceptions import MapParserError
from sys import stderr
import os
import ctypes
from typing import List

from Utils import Drone

CONFIG_PATH = "./config.toml"

RUN_ANIMATION = False
TURN: int = 0
ALL_ARRIVED: bool = False

MOVED_DRONES: List[Drone] = []
SOLUTION: List[List[str]]

SPEED: float = 1

RESET: bool = False

IS_KEY_DOWN = False

def cli_argument_parser() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fly-In")
    parser.add_argument(
        "-m", "--map", type=str,
        default="./Maps/custom/project_title.txt",
        help="path to map configuration file")

    return parser.parse_args()


@mlx_loop_hook_func
def movement_animation(param: int) -> None:
    global MOVED_DRONES
    global ALL_ARRIVED
    global TURN
    global RESET

    window: MlxVisualizer = ctypes.cast(param, ctypes.py_object).value

    if RESET:
        RESET = False
        ALL_ARRIVED = False
        window._reset_drones_position()
        TURN = 0


    if not RUN_ANIMATION or ALL_ARRIVED : return

    MOVED_DRONES = window._get_moved_drones(TURN)

    if RUN_ANIMATION:
        for drone in MOVED_DRONES:
            print(drone.id)
            drone._move_toward(SPEED)

    if all([d._has_arrived() for d in MOVED_DRONES]):
        TURN += 1
    if TURN >= len(window.solution):
        ALL_ARRIVED = True


@mlx_loop_hook_func
def handel_input(param: int) -> None:
    global SPEED
    global RESET

    mlx_ptr = ctypes.cast(param, ctypes.POINTER(mlx_t))
    if (mlx.mlx_is_key_down(mlx_ptr, MLX_KEY_E)):
        os._exit(0)
    elif (mlx.mlx_is_key_down(mlx_ptr, MLX_KEY_R)):
        RESET = True
    elif (mlx.mlx_is_key_down(mlx_ptr, MLX_KEY_LEFT)):
        if SPEED > 0.5:
            SPEED -= 0.5
    elif (mlx.mlx_is_key_down(mlx_ptr, MLX_KEY_RIGHT)):
        if (SPEED < 6):
            SPEED += 0.5
    elif (mlx.mlx_is_key_down(mlx_ptr, MLX_KEY_SPACE)):
        global RUN_ANIMATION

        if not RUN_ANIMATION:
            RUN_ANIMATION = True
        else:
            RUN_ANIMATION = False


def main() -> None:
    print("\033[H\033[J")
    args = cli_argument_parser()
    try:
        global WINDOW
        window_config = WindowConfig._from_file(CONFIG_PATH)
        print(window_config.title)
        print(window_config.x_gap)
        map_data: MapParser = MapParser.from_file(args.map)

        WINDOW = MlxVisualizer(CONFIG_PATH, map_data)

        WINDOW.init_window()
        WINDOW.init_map()
        WINDOW.solution = [
    ["D1-gate", "D2-gate", "D3-gate", "D4-gate", "D5-gate", "D6-gate", "D7-start", "D8-start", "D9-start", "D10-start", "D11-start", "D12-start"],
    ["D1-gate", "D2-gate", "D3-gate", "D4-gate", "D5-gate", "D6-gate"],
    ["D1-A3", "D2-A2", "D3-A1", "D4-A1", "D7-gate", "D8-gate", "D9-gate", "D10-gate"],
    ["D1-A3", "D2-A2", "D3-A1", "D4-A1", "D7-gate", "D8-gate", "D9-gate", "D10-gate", "D11-gate", "D12-gate"],
    ["D1-B2", "D2-B2", "D3-B1", "D4-B1", "D5-A3", "D6-A2", "D7-A1", "D8-A1", "D11-gate", "D12-gate"],
    ["D1-E", "D2-E", "D3-N1", "D4-B2", "D5-A3", "D6-A2", "D7-A1", "D8-A1"],
    ["D3-E", "D4-E", "D5-B2", "D6-B2", "D7-B1", "D8-B1", "D9-A3", "D10-A2", "D11-A1", "D12-A1"],
    ["D5-E", "D6-E", "D7-N1", "D8-B2", "D9-A3", "D10-A2", "D11-A1", "D12-A1"],
    ["D7-E", "D8-E", "D9-B2", "D10-B2", "D11-B1", "D12-B1"],
    ["D9-E", "D10-E", "D11-N1", "D12-B2"],
    ["D11-E", "D12-E"],
]

        mlx.mlx_loop_hook(WINDOW.mlx_ptr, handel_input,
                          ctypes.cast(WINDOW.mlx_ptr, c_void_p))

        mlx.mlx_loop_hook(WINDOW.mlx_ptr, movement_animation,
                          ctypes.cast(id(WINDOW), c_void_p))
        mlx.mlx_loop(WINDOW.mlx_ptr)
    except ValueError as e:
        print(e, file=stderr)
        exit(1)


if __name__ == "__main__":
    main()
