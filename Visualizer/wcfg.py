from pydantic import BaseModel


class WCfg(BaseModel):
    title: str = "Fly-in"
    resizing: bool = True
    min_width: int = 500
    bg_color: int = 0x000013ff
    bg_points_effect: int = 0xCECECEFF
    text_color: int = 0xffffffff
    enable_hub_name: bool = True
    enable_connection_txt: bool = True
    x_gap: int = 42
    y_gap: int = 92
    padding_x: int = 64
    padding_y: int = 120
