from pydantic import BaseModel
import tomllib


class WindowConfig(BaseModel):
    """
    Configuration for the application window.

    Attributes:
        title (str): The title of the window.
        resizing (bool): Whether the window can be resized.
        min_width (int): The minimum width of the window.
        bg_color (int): The background color of the window.
        bg_points_effect (int): The background points effect.
        font_color (int): The color of the font.
        banner_color (int): The color of the banner.
        enable_hub_name (bool): Whether to enable hub names.
        enable_connection_txt (bool): Whether to enable connection text.
        enable_drones_path (bool): Whether to enable drone paths.
        x_gap (int): The horizontal gap between elements.
        y_gap (int): The vertical gap between elements.
        padding_x (int): The horizontal padding of the window.
        padding_y (int): The vertical padding of the window.

    """
    title: str = "Fly-in"

    resizing: bool = True
    min_width: int = 500

    bg_color: int = 0x000013ff
    bg_points_effect: int = 0xCECECEFF

    font_color: int = 0xffffffff
    banner_color: int = 0xffffffff

    enable_hub_name: bool = False
    enable_connection_txt: bool = True

    enable_drones_path: bool = True

    x_gap: int = 42
    y_gap: int = 92
    padding_x: int = 64
    padding_y: int = 120

    @staticmethod
    def _from_file(file_path: str) -> "WindowConfig":
        """ Load the window configuration from a TOML file. """

        with open(file_path, 'rb') as f:
            content = tomllib.load(f)

        return WindowConfig(**content["window"], **content["map"])
