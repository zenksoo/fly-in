from typing import List, Dict, Any, Optional
from CExeptions import MapParserError
import re
import io


class WCfgParser:
    pass

class MapParser:
    def __new__(cls, *args, **kwargs):
        raise TypeError(f"'{cls.__name__}' is a static utility class and cannot be instantiated.")


    @staticmethod
    def _validated_mapfile(map_file: str | io.TextIOWrapper) -> io.TextIOWrapper:
        file: io.TextIOWrapper
        try:
            if isinstance(map_file, str):
                file = open(map_file, 'r')
            elif isinstance(map_file, io.TextIOWrapper):
                file = map_file
            else:
                raise ValueError(
                    "Invalid Input for MapParser, input must be path to" \
                    " file or the opened file\n\tEx: - '/maps/easy/01_linear_path.txt\n\t"\
                    "    - io.TextIOWrapper file opened using open()")
        except (ValueError, OSError, Exception) as e:
            raise MapParserError(e)

        return file

    @staticmethod
    def _metadata_pattern(line: str) -> None:
        if line.count("[") > line.count("]"):
            raise MapParserError("Missing Closing brackets")
        if line.count("[") < line.count("]"):
            raise MapParserError("Missing Open brackets")
        if re.findall(r"(\w+)\s*=\s*(\w+)\s*", line):
            raise MapParserError("Additionall Properties must be inside brackets `[]`")
        if (len(re.findall(r"(\s+\d+)", line)) > 2 or
            not re.search(r"(\s+\d+\s*)$", line)):
            raise MapParserError(f"Invalid Line")

    @staticmethod
    def _ndrones_handler(line: str) -> int:
        ndrones_pattern = re.compile(r"^nb_drones:\s*(?P<num>(-?\d+)$)?")
        ndrones_match = ndrones_pattern.match(line)

        if ndrones_match:
            if not ndrones_match.group("num"):
                raise MapParserError("Missing Number of Drones")
            n = int(ndrones_match.group(1))
        else:
            raise MapParserError("tzz")

        if n <= 0:
            raise MapParserError("Number of drones must be greater than or equall 0")
        return (n)

    @staticmethod
    def _hub_handler(line: str) -> Dict[str, Any]:

        def _parse_hub_metadata(data: str) -> Dict[str, Any]:
            attributes = {
                'color': 'green',
                'max_drones': 1,
                'zone': "normal"
            }
            if not data:
                return attributes
            match = re.findall(r"(\w+)\s*=\s*(\w+)\s*", data)
            for key, val in match:
                    attributes[key] = val
            return attributes

        def _find_missing_properties(line: str) -> None:
            # this function searsh for missing element that make the match invalid and raise MapParserError
            hub_pattern = re.compile(
                r"^(?P<type>\w+_hub|hub):\s*"
                r"(?P<name>\w+)")

            hub_name = hub_pattern.match(line)
            if not hub_name:
                raise MapParserError("Missing Hub Name")
            else:
                try:
                    int(hub_name.group("name"))
                    raise MapParserError(f"Invalid Hub name `{hub_name.group("name")}`")
                except ValueError:
                    pass

            hub_pattern = re.compile(
                r"^(?P<type>\w+_hub|hub):\s*"
                r"(?P<name>\w+)"
                r"(?P<x>\s+-?\d+)"
                r"(?P<y>\s+-?\d+)?"
                )

            hub_name = hub_pattern.match(line)
            if not hub_name:
                raise MapParserError("Missing Hub Coordinate (x, y)")
            elif not hub_name.group("y"):
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
            if not hub["metadata"]:
                MapParser._metadata_pattern(line)
            hub["metadata"] = _parse_hub_metadata(hub["metadata"])
        else:
            _find_missing_properties(line)
        return hub

    @staticmethod
    def _connections_handler(line: str, valid_hubs: List[str]) -> None:
        print(line)
        connection_pattern = re.compile(
            r"^connection\s*:\s+"
            r"(?P<fc>\w+)"
            r"(?P<sep>-)"
            r"(?P<lc>\w+)"
            r'(?:\s+\[(?P<metadata>.*)\])?'
            )


        connection_match = connection_pattern.match(line)
        if connection_match:
            data = connection_match.groupdict()
            print(data)
            if not data["metadata"]:
                MapParser._metadata_pattern(line)
            data["metadata"]

    @classmethod
    def parse(cls, mapfile_path: str | io.TextIOWrapper
              ) -> Dict[str, int | List[Any]]:
        map_file: io.TextIOWrapper = cls._validated_mapfile(mapfile_path)
        parsed_data: Dict[str, Any] = {
            "ndrones": 1,
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
                    raise MapParserError(f"Invalid Line '{line}'")
            except MapParserError as e:
                raise MapParserError(f"Line {i + 1}: {e}")

        # print(parsed_data)
        return parsed_data




