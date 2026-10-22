from pydantic import BaseModel, Field, ConfigDict
from .Types import ZoneTypes, HubType, Colors
from typing import Tuple
from MLX.libmlx import mlx_image_t


class Drone():
    """
        Class representing a drone in the simulation.
    """
    def __init__(self, id: str) -> None:
        self.id = id
        self.position: Tuple[float, float]
        self.dest_pos: Tuple[float, float]
        self.dest_hub: Hub | None
        self.color: Colors
        self.mlximg: mlx_image_t
        self.step: Tuple[float, float] = (0.0, 0.0)


class HubMetaData(BaseModel):
    """
        Class representing metadata for a hub.
    """
    color: Colors = Colors.green
    zone: ZoneTypes = ZoneTypes.normal
    max_drones: int = Field(default=1, gt=0)


class HUBGfx(BaseModel):
    """
        Class representing graphical properties for a hub.
    """
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
    """
        Class representing a hub in the simulation.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    name: str
    type: HubType
    droneCount: int = 0
    x: int
    y: int
    mlx_img: mlx_image_t | None = None
    metadata: HubMetaData = HubMetaData()
    gfx: HUBGfx = HUBGfx()
    visited: bool = False


class ConnectionMetadata(BaseModel):
    """
        Class representing metadata for a connection between hubs.
    """
    max_link_capacity: int = Field(default=1, gt=0)


class Connection(BaseModel):
    """
        Class representing a connection between two hubs.
    """
    start: str
    end: str
    metadata: ConnectionMetadata = ConnectionMetadata()
