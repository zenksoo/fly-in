



def pack_rgba(r: int, g: int, b:int , a: int) -> int:
        return (r << 24) | (g << 16) | (b << 8) | a


def HexColor_to_decimal(hex_color: str) -> int:
    return pack_rgba(
        int(hex_color[1:3], 16),
        int(hex_color[3:5], 16),
        int(hex_color[5:7], 16),
        int(hex_color[7:9], 16) if len(hex_color) > 7 else 255
    )
