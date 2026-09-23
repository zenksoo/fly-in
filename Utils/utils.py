from pydantic import BaseModel, Field, ConfigDict
from .Types import ZoneTypes, HubType, Colors
from typing import Tuple
from MLX.libmlx import mlx_image_t
import random

def pack_rgba(r: int, g: int, b: int, a: int) -> int:
    return (r << 24) | (g << 16) | (b << 8) | a


def HexColor_to_decimal(hex_color: str) -> int:
    valid_char = "#0123456789ABCDEFabcdef"

    for hex in hex_color:
        if hex not in valid_char:
            raise ValueError(f"Invalid Hex Decimal Format `{hex_color}`")

    if len(hex_color) == 4 or len(hex_color) == 5:
        return pack_rgba(
            int(hex_color[1:2] * 2, 16),
            int(hex_color[2:3] * 2, 16),
            int(hex_color[3:4] * 2, 16),
            int(hex_color[4:5] * 2, 16) if len(hex_color) > 4 else 255
        )
    elif len(hex_color) == 7 or len(hex_color) == 9:
        return pack_rgba(
            int(hex_color[1:3], 16),
            int(hex_color[3:5], 16),
            int(hex_color[5:7], 16),
            int(hex_color[7:9], 16) if len(hex_color) > 7 else 255
        )
    else:
        raise ValueError(
            "Invalid HexDecimal Value, (e.g #fff #ffffff #ffff #ffffffff)")

class KinematicEntity2D:
    def __init__(self, id: str) -> None:
        self.id = id
        self.position: Tuple[float, float]
        self.distination: Hub
        self.color: Colors
        self.arrived: bool = False
        self.mlximg: mlx_image_t

    def _get_vector_direction_to(self) -> Tuple[float, float]:

        sx = self.distination.x - self.position[0]
        sy = self.distination.y - self.position[1]

        step = max(abs(sx), abs(sy))

        dx = sx / step
        dy = sy / step

        return (dx, dy)

    def _move_toward(self, SPEED: float = 1.0) -> None:

        if self._has_arrived():
            return

        direction = self._get_vector_direction_to()

        img_w, img_h = (self.mlximg.contents.width, self.mlximg.contents.height)

        new_pos_x = self.position[0] + direction[0] * SPEED * (random.random())
        new_pos_y = self.position[1] + direction[1] * SPEED * (random.random())


        self.position = (new_pos_x, new_pos_y)

        self.mlximg.contents.instances[0].x = round(self.position[0]) - img_w // 2
        self.mlximg.contents.instances[0].y = round(self.position[1]) - img_h // 2

    def _has_arrived(self) -> bool:
        x, y = (self.position[0], self.position[1])

        if ((x >= self.distination.x - 5 and x <= self.distination.x + 5) and
            (y >= self.distination.y - 5 and y <= self.distination.y + 5)):
            if not self.arrived:
                self.distination.droneCount += 1
                self.arrived = True
            return True
        return False


class Drone(KinematicEntity2D):
    def __init__(self, id: str) -> None:
        super().__init__(id)



class HubMetaData(BaseModel):
    color: Colors = Colors.green
    zone: ZoneTypes = ZoneTypes.normal
    max_drones: int = Field(default=1, gt=0)


class HUBGfx(BaseModel):
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
    droneCount: int = 0
    x: int
    y: int
    mlx_img: mlx_image_t | None = None
    metadata: HubMetaData = HubMetaData()
    gfx: HUBGfx = HUBGfx()


class ConnectionMetadata(BaseModel):
    max_link_capacity: int = Field(default=1, gt=0)


class Connection(BaseModel):
    start: str
    end: str
    metadata: ConnectionMetadata = ConnectionMetadata()
