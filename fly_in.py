from MLX.libmlx import mlx, c_void_p
import argparse
from Visualizer import MlxVisualizer
from CExceptions import MapParserError
from Parser import MapParser
from sys import stderr
import ctypes
from PathFinding import PathFinding
from Simulation import DroneSimulation
from typing import List

CONFIG_PATH = "./config.toml"

def cli_argument_parser() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fly-In")
    parser.add_argument(
        "-m", "--map", type=str,
        default="./Maps/custom/project_title.txt",
        help="path to map configuration file")

    return parser.parse_args()


class FlyIn:
    args: argparse.Namespace
    visualizer: MlxVisualizer
    simulation: DroneSimulation
    map_data: MapParser

    @classmethod
    def _full_setup(cls) -> None:
        cls.map_data = MapParser.from_file(cls.args.map)

        cls.simulation = DroneSimulation(cls.map_data)
        cls.visualizer = MlxVisualizer(CONFIG_PATH, cls.simulation)

        cls.visualizer.init_window()
        cls.visualizer.init_map()

        tt = PathFinding.plan_all_drones(cls.simulation.drones,
                                           cls.map_data.connections,
                                           cls.map_data.hubs)

        print(tt)
        print(len(tt))
        cls.simulation.solution = tt

        cls.visualizer._update_hub_capacity_label()

        cls.simulation._update_moved_drones()


def main() -> None:
    print("\033[H\033[J")
    FlyIn.args = cli_argument_parser()
    # try:
    FlyIn._full_setup()

    mlx.mlx_loop_hook(FlyIn.visualizer.mlx_ptr,
                        FlyIn.simulation.movement_animation,
                        ctypes.cast(id(FlyIn.visualizer), c_void_p))

    mlx.mlx_key_hook(FlyIn.visualizer.mlx_ptr,
                        FlyIn.visualizer.handel_input,
                        ctypes.cast(id(FlyIn.visualizer), c_void_p))

    mlx.mlx_loop(FlyIn.visualizer.mlx_ptr)
    # except BaseException as e:
    #     print(e, file=stderr)
    #     exit(1)


if __name__ == "__main__":
    main()
