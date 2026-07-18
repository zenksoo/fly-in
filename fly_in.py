from MLX.libmlx import mlx
import argparse
from Visualizer import MlxWindow
from Parser import MapParser
from CExceptions import MapParserError


def cli_argument_parser() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="tzzz")
    parser.add_argument(
        "-m", "--map", type=str,
        default="./maps/easy/03_basic_capacity.txt",
        help="path to map configuration file")

    return parser.parse_args()


def main():
    args = cli_argument_parser()
    try:
        map: MapParser = MapParser.from_file(args.map)

        mlx_window = MlxWindow("./config.toml")

        mlx_ptr = mlx_window.init(map)

        mlx.mlx_loop(mlx_window.mlx_ptr)
    except MapParserError as e:
        print(e)


if __name__ == "__main__":
    main()
