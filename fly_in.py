from MLX.libmlx import mlx, mlx_t, mlx_loop_hook_func, c_void_p
from MLX.libmlx import MLX_KEY_E, MLX_KEY_RIGHT, MLX_KEY_LEFT, MLX_KEY_SPACE
import argparse
from Visualizer import MlxWindow
from Parser import MapParser
from CExceptions import MapParserError
from sys import stderr
import os
import ctypes


CONFIG_PATH = "./config.toml"


def cli_argument_parser() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fly-In")
    parser.add_argument(
        "-m", "--map", type=str,
        default="./Maps/custom/project_title.txt",
        help="path to map configuration file")

    return parser.parse_args()


@mlx_loop_hook_func
def handel_input(param: int) -> None:
    mlx_ptr = ctypes.cast(param, ctypes.POINTER(mlx_t))
    if (mlx.mlx_is_key_down(mlx_ptr, MLX_KEY_E)):
        os._exit(0)
    elif (mlx.mlx_is_key_down(mlx_ptr, MLX_KEY_RIGHT)):
        print("right")
    elif (mlx.mlx_is_key_down(mlx_ptr, MLX_KEY_LEFT)):
        print("left")

    elif (mlx.mlx_is_key_down(mlx_ptr, MLX_KEY_SPACE)):
        print("tuggle animation")


def main() -> None:
    print("\033[H\033[J")
    args = cli_argument_parser()
    try:
        map_data: MapParser = MapParser.from_file(args.map)

        window = MlxWindow(CONFIG_PATH)

        window.init_window(map_data)
        solution = [["D1-waypoint1"]]

        window.engine(map_data, solution)


        mlx.mlx_loop_hook(window.mlx_ptr, handel_input,
                          ctypes.cast(window.mlx_ptr, c_void_p))
        mlx.mlx_loop(window.mlx_ptr)
    except BaseException as e:
        print(e, file=stderr)
        exit(1)


if __name__ == "__main__":
    main()
