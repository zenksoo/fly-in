from MLX.libmlx import mlx, c_void_p
import argparse
from Visualizer import MlxVisualizer, WindowConfig
from Parser import MapParser
from sys import stderr
import ctypes
from Simulation import DroneSimulation


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

        cls.simulation.solution = [
    ["D1-start-gate", "D2-start-gate", "D3-start-gate", "D4-start-gate", "D5-start-gate", "D6-start-gate", "D7-start", "D8-start", "D9-start", "D10-start", "D11-start", "D12-start"],
    ["D1-gate", "D2-gate", "D3-gate", "D4-gate", "D5-gate", "D6-gate"],
    ["D1-gate-A3", "D2-gate-A2", "D3-gate-A1", "D4-gate-A1", "D7-start-gate", "D8-start-gate", "D9-start-gate", "D10-start-gate"],
    ["D1-A3", "D2-A2", "D3-A1", "D4-A1", "D7-gate", "D8-gate", "D9-gate", "D10-gate", "D11-start-gate", "D12-start-gate"],
    ["D1-B2", "D2-B2", "D3-B1", "D4-B1", "D5-gate-A3", "D6-gate-A2", "D7-gate-A1", "D8-gate-A1", "D11-gate", "D12-gate"],
    ["D1-E", "D2-E", "D3-N1", "D4-B2", "D5-A3", "D6-A2", "D7-A1", "D8-A1"],
    ["D3-E", "D4-E", "D5-B2", "D6-B2", "D7-B1", "D8-B1", "D9-gate-A3", "D10-gate-A2", "D11-gate-A1", "D12-gate-A1"],
    ["D5-E", "D6-E", "D7-N1", "D8-B2", "D9-A3", "D10-A2", "D11-A1", "D12-A1"],
    ["D7-E", "D8-E", "D9-B2", "D10-B2", "D11-B1", "D12-B1"],
    ["D9-E", "D10-E", "D11-N1", "D12-B2"],
    ["D11-E", "D12-E"],
        ]

        cls.visualizer._update_hub_capacity_label()

        cls.simulation._update_moved_drones()




def main() -> None:
    print("\033[H\033[J")
    FlyIn.args = cli_argument_parser()
    try:
        FlyIn._full_setup()
#         # map_data: MapParser = MapParser.from_file(args.map)

#         # simulation = DroneSimulation(map_data)

#         # visualizer = MlxVisualizer(CONFIG_PATH)

#         # visualizer.simulation = simulation

# #         visualizer.init_window()
# #         visualizer.init_map()
# #         simulation.solution =
# # ]

#         # window.solution = [
#         #     ["D1-waypoint1", "D2-waypoint1"],
#         #     ["D1-waypoint2", "D2-waypoint2"],
#         #     ["D1-goal", "D2-goal"]
#         # ]
#         visualizer._update_hub_capacity_label()

#         simulation._update_moved_drones()


        mlx.mlx_loop_hook(FlyIn.visualizer.mlx_ptr, FlyIn.simulation.movement_animation,
                          ctypes.cast(id(FlyIn.visualizer), c_void_p))

        mlx.mlx_key_hook(FlyIn.visualizer.mlx_ptr, FlyIn.visualizer.handel_input,
                         ctypes.cast(id(FlyIn.visualizer), c_void_p))

        mlx.mlx_loop(FlyIn.visualizer.mlx_ptr)
    except ValueError as e:
        print(e, file=stderr)
        exit(1)


if __name__ == "__main__":
    main()
