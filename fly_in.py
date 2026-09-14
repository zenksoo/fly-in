from MLX import mlx, MLX_KEY_E
import argparse
from Visualizer import MlxWindow
from Parser import MapParser
from CExceptions import MapParserError
from sys import stderr
import signal
import os


CONFIG_PATH = "./config.toml"

def cli_argument_parser() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fly-In")
    parser.add_argument(
        "-m", "--map", type=str,
        default="./Maps/custom/project_title.txt",
        help="path to map configuration file")

    return parser.parse_args()




def main() -> None:
    print("\033[H\033[J")
    args = cli_argument_parser()
    try:
        map_data: MapParser = MapParser.from_file(args.map)


        window = MlxWindow(CONFIG_PATH)

        window.init(map_data)
        # def test(sig, frame):



        solution = [["D1-waypoint1"]]

        window.engine(map_data, solution)
        # signal.signal(signal.SIGINT, test)
        if (mlx.mlx_is_key_down(window.mlx_ptr, MLX_KEY_E)):
            print("tzzzz", flush=True)
        mlx.mlx_loop(window.mlx_ptr)
    except MapParserError as e:
        print(e, file=stderr)
        exit(1)


if __name__ == "__main__":
    main()
