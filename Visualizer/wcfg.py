import tomllib
from pydantic import BaseModel


class WCfg(BaseModel):
    title: str = "Fly-in"
    min_width: int = 500
    bg_color: int = (0xFFFFFF04 << 8) + 0xff


class HubCfg(BaseModel):
    show_name: bool = True
    text_color: int = (0xffffff << 8) + 0xff


class ConnectionCfg(BaseModel):
    show_capacity: bool = True
    text_color: int = (0xffffff << 8) + 0xff


class Sizing(BaseModel):
    space: int = 50
    padding_x: int = 40
    padding_y: int = 120


class Cfg(BaseModel):
    window: WCfg = WCfg()
    hub: HubCfg = HubCfg()
    connection: ConnectionCfg = ConnectionCfg()
    sizing: Sizing = Sizing()
