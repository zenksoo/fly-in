from MLX.libmlx import mlx
import argparse
from Visualizer import MlxWindow
from Parser import MapParser
from CExceptions import MapParserError


CONFIG_PATH = "./config.toml"


def cli_argument_parser() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="tzzz")
    parser.add_argument(
        "-m", "--map", type=str,
        default="./maps/custom/project_title.txt",
        help="path to map configuration file")

    return parser.parse_args()


def main():
    args = cli_argument_parser()
    try:
        map_data: MapParser = MapParser.from_file(args.map)

        window = MlxWindow(CONFIG_PATH)

        mlx_ptr = window.init(map_data)

        mlx.mlx_loop(window.mlx_ptr)
    except MapParserError as e:
        print(e)


if __name__ == "__main__":
    main()
