from pydantic import BaseModel
import tomllib

class WindowConfig(BaseModel):
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
        with open(file_path, 'rb') as f:
            content = tomllib.load(f)

        return WindowConfig(**content["window"], **content["map"])

