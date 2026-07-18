
from enum import Enum



from enum import Enum


class Colors(Enum):
    #  Blacks
    black = (0x000000 << 8) + 0xff


    # Whites & Off-Whites
    white = (0xFFFFFF << 8) + 0xff
    ivory = (0xFFFFF0 << 8) + 0xff
    azure = (0xF0FFFF << 8) + 0xff
    mint = (0xF5FFFA << 8) + 0xff
    lavender = (0xE6E6FA << 8) + 0xff
    beige = (0xF5F5DC << 8) + 0xff


    # Grays & Silvers
    silver = (0xC0C0C0 << 8) + 0xff
    gray = (0x808080 << 8) + 0xff


    # Reds, Pinks & Maroons
    red = (0xFF0000 << 8) + 0xff
    pink = (0xFFC0CB << 8) + 0xff
    tomato = (0xFF6347 << 8) + 0xff
    salmon = (0xFA8072 << 8) + 0xff
    crimson = (0xDC143C << 8) + 0xff
    brown = (0xA52A2A << 8) + 0xff
    maroon = (0x800000 << 8) + 0xff


    # Warm Browns
    orange = (0xFFA500 << 8) + 0xff
    coral = (0xFF7F50 << 8) + 0xff
    wheat = (0xF5DEB3 << 8) + 0xff
    chocolate = (0xD2691E << 8) + 0xff
    tan = (0xD2B48C << 8) + 0xff


    # Golds & Olives
    yellow = (0xFFFF00 << 8) + 0xff
    gold = (0xFFD700 << 8) + 0xff
    khaki = (0xF0E68C << 8) + 0xff
    olive = (0x808000 << 8) + 0xff


    # Greens & Limes
    lime = (0x00FF00 << 8) + 0xff
    aquamarine = (0x7FFFD4 << 8) + 0xff
    green = (0x008000 << 8) + 0xff


    # Cyans & Teals
    cyan = (0x00FFFF << 8) + 0xff
    turquoise = (0x40E0D0 << 8) + 0xff
    teal = (0x008080 << 8) + 0xff


    # Blues & Navies
    blue = (0x0000FF << 8) + 0xff
    navy = (0x000080 << 8) + 0xff


    # Violets & Magentas
    magenta = (0xFF00FF << 8) + 0xff
    fuchsia = (0xFF00FF << 8) + 0xff
    violet = (0xEE82EE << 8) + 0xff
    plum = (0xDDA0DD << 8) + 0xff
    orchid = (0xDA70D6 << 8) + 0xff
    indigo = (0x4B0082 << 8) + 0xff
    purple = (0x800080 << 8) + 0xff


class ZoneTypes(str, Enum):
    normal = "normal"
    blocked = "blocked"
    restricted = "restricted"
    priority = "priority"



class HubType(str, Enum):
    start_hub = "start_hub"
    hub = "hub"
    end_hub = "end_hub"
