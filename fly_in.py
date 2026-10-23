from MLX.libmlx import mlx, c_void_p
import argparse
from Visualizer import MlxVisualizer
from CExceptions import InvalidCliArgument
from Parser import MapParser
from sys import stderr
import ctypes
from PathFinding import PathFinding
from Simulation import DroneSimulation
from pathlib import Path


CONFIG_PATH = "./config.toml"


class CLIArgParser:
    """ A class for parsing command line arguments for the FlyIn program. """
    @staticmethod
    def _parse() -> argparse.Namespace:
        """ Parse the command line arguments.

        Raises:
            InvalidCliArgument: If the command line arguments are invalid.
            InvalidCliArgument: If the map file is invalid.

        Returns:
            argparse.Namespace: The parsed command line arguments.
        """
        parser = argparse.ArgumentParser(description="Fly-In")
        parser.add_argument(
            "-m", "--map", type=str,
            default="./Maps/custom/fly-in.txt",
            help="path to map configuration file")

        parser.add_argument(
            "-o", "--output", type=str,
            default="simulation_output.txt",
            help="path to drones routes solution file")

        args = parser.parse_args()

        # create path object for map
        # and output to check it's a valid path or no
        map_file = Path(args.map)
        output_file = Path(args.output)

        if not map_file.is_file():
            raise InvalidCliArgument("Invalid value for --map\n\n\t\
                                    Invalid path, does not exist,\
                                    or points to a directory.")
        if output_file.is_dir():
            raise InvalidCliArgument("Invalid Value for --output\n\n\t\
                                    Invalid path, must be path to a file\
                                    not to a directory.")
        return args


class FlyIn:
    """
    The main class for the FlyIn program. It handles the initialization
    of the simulation, visualizer, and pathfinding,
    and starts the MLX loop.
    """
    args: argparse.Namespace
    visualizer: MlxVisualizer
    simulation: DroneSimulation
    map_data: MapParser

    @staticmethod
    def display_solution(solution_file: str) -> None:
        """ Display the solution from a file.

        Args:
            solution_file (str): The path to the solution file.
        """
        with open(solution_file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                print(line)

    @classmethod
    def _generate_simulation_output(cls) -> None:
        """ Generate the simulation output file."""
        i = 1
        with open(cls.args.output, 'w') as f:
            for turn_steps in cls.simulation.solution:
                for step in turn_steps:
                    f.write(f"{step} ")
                f.write("\n")
                i += 1

    @classmethod
    def _core(cls) -> None:
        """
            The core function of the FlyIn program.
            It initializes the simulation, visualizer,
            and pathfinding, and starts the MLX loop.
        """
        cls.args = CLIArgParser._parse()
        cls.map_data = MapParser.from_file(cls.args.map)

        cls.simulation = DroneSimulation(cls.map_data)
        cls.visualizer = MlxVisualizer(CONFIG_PATH, cls.simulation)

        cls.visualizer.init_window()
        cls.visualizer.init_map()

        cls.simulation.solution = PathFinding.plan_all_drones(
            cls.simulation.drones,
            cls.map_data.connections,
            cls.map_data.hubs)

        cls._generate_simulation_output()

        cls.display_solution(cls.args.output)

        cls.visualizer._update_hub_capacity_label()

        cls.simulation._update_moved_drones()

        mlx.mlx_loop_hook(cls.visualizer.mlx_ptr,
                          cls.simulation.movement_animation,
                          ctypes.cast(id(cls.visualizer), c_void_p))

        mlx.mlx_key_hook(cls.visualizer.mlx_ptr,
                         cls.visualizer.handel_input,
                         ctypes.cast(id(cls.visualizer), c_void_p))

        mlx.mlx_loop(cls.visualizer.mlx_ptr)


if __name__ == "__main__":
    """ The main function of the FlyIn program. """
    print("\033[H\033[J")
    try:
        FlyIn._core()
    except BaseException as e:
        print(e, file=stderr)
        exit(1)
