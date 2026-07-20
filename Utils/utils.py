from pydantic import BaseModel, Field, ConfigDict
from .Types import ZoneTypes, HubType, Colors
from typing import Tuple


def pack_rgba(r: int, g: int, b: int, a: int) -> int:
    return (r << 24) | (g << 16) | (b << 8) | a


def HexColor_to_decimal(hex_color: str) -> int:
    return pack_rgba(
        int(hex_color[1:3], 16),
        int(hex_color[3:5], 16),
        int(hex_color[5:7], 16),
        int(hex_color[7:9], 16) if len(hex_color) > 7 else 255
    )


class HubMetaData(BaseModel):
    color: Colors = Colors.green
    zone: ZoneTypes = ZoneTypes.normal
    max_drones: int = Field(default=1, gt=0)


class HUBGfx:
    w: int = 0
    h: int = 0
    top_label: dict[str, Tuple[int, int]] = {
        "start": (0, 0),
        "end": (0, 0)
    }
    bottom_label: dict[str, Tuple[int, int]] = {
        "start": (0, 0),
        "end": (0, 0)
    }


class Hub(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    name: str
    type: HubType
    x: int
    y: int
    metadata: HubMetaData = HubMetaData()
    gfx: HUBGfx = HUBGfx()


class ConnectionMetadata(BaseModel):
    max_link_capacity: int = Field(default=1, gt=0)


class Connection(BaseModel):
    start: str
    end: str
    metadata: ConnectionMetadata = ConnectionMetadata()
