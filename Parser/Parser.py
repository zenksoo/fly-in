from typing import List, Dict, Any
from CExceptions import MapParserError
import re
import io


class WCfgParser:
    pass


class MapParser:
    def __init__(self, ndrones: int, hubs: List[Dict[str, Any]],
                 connections: List[Dict[str, Any]]) -> None:
        self.ndrones = ndrones
        self.hubs = hubs
        self.connections = connections

    @staticmethod
    def _validated_mapfile(map_file: str | io.TextIOWrapper
                           ) -> io.TextIOWrapper:
        file: io.TextIOWrapper
        try:
            if isinstance(map_file, str):
                file = open(map_file, 'r')
            elif isinstance(map_file, io.TextIOWrapper):
                file = map_file
            else:
                raise ValueError(
                    "Invalid Input for MapParser, input must be path to\
                    file or the opened file\n\tEx:\
                    \n\t - '/maps/easy/01_linear_path.txt\n\t\
                    - io.TextIOWrapper file opened using open()")
        except (ValueError, OSError, Exception) as e:
            raise MapParserError(e)

        return file

    @staticmethod
    def _metadata_pattern(line: str) -> None:
        if line.count("[") > line.count("]"):
            raise MapParserError(
                "missing closing bracket ']' in metadata block\n\
                \n\tmetadata block must be wrapped in brackets:\
                [propertie=value]")
        if line.count("[") < line.count("]"):
            raise MapParserError(
                "missing opening bracket '[' in metadata block\n\
                \n\tmetadata block must be wrapped in brackets:\
                [propertie=value]")
        print("[" in line)
        if (re.findall(r"(\w+)\s*=\s*(\w+)\s*", line)):
            raise MapParserError(
                "missing brackets '[]' around metadata block\n\
                \n\tmetadata block must be wrapped in brackets:\
                [propertie=value]"
            )

    @staticmethod
    def _ndrones_handler(line: str) -> int:
        ndrones_pattern = re.compile(r"^nb_drones\s*:\s*(?P<num>(-?\d+))?")
        ndrones_match = ndrones_pattern.match(line)

        if ndrones_match:
            if not ndrones_match.group("num"):
                raise MapParserError("missing value for 'nb_drones'\n\
                \n\t'nb_drones' expects a \
                positive integer (e.g. nb_drones: 4).!")

            unexpected_text = re.sub(ndrones_pattern, "", line)
            n = int(ndrones_match.group(1))

            if unexpected_text:
                raise MapParserError(
                f"unexpected token '{unexpected_text}' after value '{n}'\n\
                \n\t'nb_drones' expects a single integer, nothing more. ")
        else:
            raise MapParserError(
                "missing value for 'nb_drones'\n\
                \n\t'nb_drones' expects a positive\
                integer (e.g. nb_drones: 4).!")

        if n <= 0:
            raise MapParserError(f"invalid value '{n}' for 'nb_drones'\n\
            \n\t'nb_drones' must be a positive integer greater than zero.")
        return (n)

    @staticmethod
    def _hub_handler(line: str) -> Dict[str, Any]:

        def _parse_hub_metadata(data: str) -> Dict[str, Any]:
            attributes = {
                'color': 'none',
                'max_drones': 1,
                'zone': "normal"
            }
            if not data:
                return attributes
            match = re.findall(r"(\w+)=(\w+)\s*", data)

            unexpected_text = re.sub(r"(\w+)=(\w+)", '', data).strip()
            if unexpected_text:
                raise MapParserError(
                    f"invalid properties syntax `'{"' '".join(unexpected_text.split(" "))}'`\
                    in hub meatadata\n\
                    \n\tProperties must follow 'key=value' format: [color=green max_drones=2]"
                )
            for key, val in match:
                if not key in attributes:
                    raise MapParserError(
                        f"unknown property '{key}' in hub metadata\n\
                        \n\tValid metadata for 'hub': 'color', 'max_drones', 'zone'"
                    )
                attributes[key] = val
            try:
                attributes["max_drones"] = int(attributes["max_drones"])
            except ValueError:
                attributes["max_drones"] = 1
            return attributes

        def _find_missing_properties(line: str) -> None:
            # this function searsh for missing element that make the match invalid and raise MapParserError
            hub_pattern = re.compile(
                r"^(?P<type>\w+_hub|hub):\s*"
                r"(?P<name>\w+)")

            match = hub_pattern.match(line)
            if not match:
                raise MapParserError("Missing Hub Name")

            hub_pattern = re.compile(
                r"^(?P<type>\w+_hub|hub):\s*"
                r"(?P<name>\w+)"
                r"(?P<x>\s+-?\d+)"
                r"(?P<y>\s+-?\d+)?"
                )

            match = hub_pattern.match(line)
            if not match:
                raise MapParserError("Missing Hub Coordinate (x, y)")
            elif not match.group("y"):
                raise MapParserError("Missing y axis coordinate for hub")

        hub: Dict[str, Any] = {}
        hub_pattern = re.compile(
                r"^(?P<type>\w+_hub|hub):\s*"
                r"(?P<name>\w+)"
                r"(?P<x>\s+-?\d+)"
                r"(?P<y>\s+-?\d+)"
                r'(?:\s+\[(?P<metadata>.*)\])?'
                )



        hub_match = hub_pattern.match(line)

        if hub_match:
            hub = hub_match.groupdict()
            hub["x"] = int(hub["x"])
            hub["y"] = int(hub["y"])

            unexpected_text = re.sub(hub_pattern, "", line)
            unexpected_text = re.sub(r"(?:\s+\[.*=.*\])", "", unexpected_text)
            unexpected_text = re.sub(r"(?:\[?\w+=\w+\]?)", "", unexpected_text).strip()
            if unexpected_text:
                raise MapParserError(
                    f"unexpected tokens `'{"' '".join(unexpected_text.split(" "))}'`\n\
                    \n\t'hub' expects: hub: <name> <x> <y> [metadata]")
            if not hub["metadata"]:
                MapParser._metadata_pattern(line)
            hub["metadata"] = _parse_hub_metadata(hub["metadata"])
        else:
            _find_missing_properties(line)
            add = re.sub(hub_pattern, '', line)
            add = re.sub(r"(?:\s+\[.*\])", '', add)
            if add:
                raise MapParserError(f"Invalid Line, Additionall Items `{add}`")
        return hub

    @staticmethod
    def _connections_handler(line: str, valid_hubs: List[str]) -> Dict[str, Any]:

        def _parse_connection_metadata(data: str) -> Dict[str, Any]:
            attributes = {
                "max_link_capacity": 1
            }
            if not data:
                return attributes
            match = re.findall(r"(\w+)\s*=\s*(\w+)\s*", data)
            for key, val in match:
                    if key not in attributes.keys():
                        raise MapParserError(f"Unregistred Key `{key}`")
                    try:
                        attributes[key] = int(val)
                    except ValueError:
                        raise MapParserError("max_link_capacity Must be valid Integer")
            return attributes

        connection_pattern = re.compile(
            r"^connection\s*:\s+"
            r"(?P<fc>\w+)"
            r"(?P<sep>-)"
            r"(?P<lc>\w+)"
            r'(?:\s+\[(?P<metadata>.*)\])?'
            )


        connection_match = connection_pattern.match(line)
        connection: Dict[str, Any] = {}
        if connection_match:
            data = connection_match.groupdict()
            if data["fc"] not in valid_hubs:
                raise MapParserError(f"Invalid Hub Name `{data["fc"]}`")
            if data["lc"] not in valid_hubs:
                raise MapParserError(f"Invalid Hub Name `{data["lc"]}`")
            if not data["metadata"]:
                MapParser._metadata_pattern(line)
            connection["from"] = data["fc"]
            connection["to"] = data["lc"]
            connection["metadata"] = _parse_connection_metadata(data["metadata"])
        return connection

    @classmethod
    def parse(cls, mapfile_path: str | io.TextIOWrapper
              ) -> "MapParser":
        map_file: io.TextIOWrapper = cls._validated_mapfile(mapfile_path)
        parsed_data: Dict[str, Any] = {
            "hubs": [],
            "connections": []
        }

        file_content = map_file.readlines()

        for line, i in zip(file_content, range(len(file_content))):
            if line.startswith("#") or not len(line.strip()):
                continue
            line = line.split("#")[0].strip()

            try:
                if re.match(r"^nb_drones", line):
                    parsed_data["ndrones"] = cls._ndrones_handler(line)
                elif re.match(r"^(?P<type>\w+_hub|hub):\s*", line):
                    parsed_data["hubs"].append(cls._hub_handler(line))
                elif re.match(r"^connection", line):
                    valid_hubs = [hub["name"] for hub in parsed_data["hubs"]]
                    parsed_data["connections"].append(cls._connections_handler(line, valid_hubs))
                else:
                    raise MapParserError(f"unrecognized syntax\n\
                    \n\tExpected one of: 'nb_drones', 'start_hub', 'hub', 'end_hub', 'connection'")
            except MapParserError as e:
                raise MapParserError(f"MapParserError: Line {i + 1}: {e}")

        map_file.close()

        if not parsed_data.get("ndrones"):
            raise MapParserError("Missing Required Line for Number of drones `nb_drones: <positive_integer>`")


        return MapParser(parsed_data["ndrones"],
                         parsed_data["hubs"],
                         parsed_data["connections"])




