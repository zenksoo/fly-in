import tomllib
from pydantic import BaseModel


class WCfg(BaseModel):
    title: str = "Fly-in"
    min_width: int = 500
    bg_color: int = 0x000013ff
    text_color: int = 0xffffffff
    enable_hub_name: bool = True
    enable_connection_txt: bool = True
    x_gap: int = 42
    y_gap: int = 92
    padding_x: int = 64
    padding_y: int = 120
