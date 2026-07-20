from CExceptions import MapParserError, MetaDataParserError
from Utils import (Hub, HubMetaData, Connection,
                   ConnectionMetadata, ZoneTypes, Colors)
from typing import List, Dict, Any
from pydantic import ValidationError

import re
import io


class MapParser:
    def __init__(self, ndrones: int, hubs: Dict[str, Hub],
                 connections: List[Connection]) -> None:
        self.ndrones = ndrones
        self.hubs = hubs
        self.connections = connections

    @staticmethod
    def _validated_mapfile(
                           map_file: str | io.TextIOWrapper
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
    def _metadata_pattern(pattern: re.Pattern, match: re.Match) -> None:
        match_source = re.sub(pattern, "", match.string).strip()
        match_source = re.sub(r'\s+', " ", match_source)
        metadata_content = re.findall(r"(\w+=\w+)", match_source)
        metadata_pattern = re.compile(
            r"(?P<open>\[)?"
            f"{" ".join(metadata_content)}"
            r"(?P<close>\])?")

        match = metadata_pattern.match(match_source)  # type: ignore

        if match and metadata_content:
            if not match.group("open") and not match.group("close"):
                raise MapParserError(
                    "missing brackets '[]' around metadata block\n\
                    \n\tmetadata block must be wrapped in brackets:\
                    [propertie=value]")
            elif not match.group("open"):
                raise MapParserError(
                    "missing opening bracket '[' in metadata block\n\
                    \n\tmetadata block must be wrapped in brackets:\
                    [propertie=value]"
                )
            else:
                raise MapParserError(
                    "missing closing bracket ']' in metadata block\n\
                    \n\tmetadata block must be wrapped in brackets:\
                    [propertie=value]"
                )

    @staticmethod
    def _metadata_parser(metadata_for: str, data: str
                         ) -> HubMetaData | ConnectionMetadata | None:
        if not data:
            if metadata_for == "hub":
                return HubMetaData()
            elif metadata_for == "connection":
                return ConnectionMetadata()

        registred_metadata = ['color', 'max_drones',
                              'zone', "max_link_capacity"]
        metadata_dict: Dict[str, Any] = {}

        data = data[2: len(data) - 1]
        match = re.findall(r"(\w+)=(-?\w+)\s*", data)

        unexpected_text = re.sub(r"(\w+)=(-?\w+)", '', data).strip()

        if unexpected_text:
            raise MapParserError(
                f"invalid properties syntax\
                `'{"' '".join(unexpected_text.split(" "))}'`\
                in meatadata\n\
                \n\tProperties must follow 'key=value' format: [color=green]"
            )

        for key, val in match:
            if key not in registred_metadata:
                raise MetaDataParserError(
                    f"unknown metadata property '{key}'\n")
            if key == "zone":
                metadata_dict[key] = ZoneTypes[val]
            elif key == "color":
                metadata_dict[key] = Colors[val]
            else:
                metadata_dict[key] = int(val)

        if metadata_for == "hub":
            return HubMetaData(**metadata_dict)
        elif metadata_for == "connection":
            return ConnectionMetadata(**metadata_dict)

        return None

    @staticmethod
    def _ndrones_handler(nd_match: re.Match) -> int:
        if not nd_match.group("num"):
            raise MapParserError("missing value for 'nb_drones'\n\
            \n\t'nb_drones' expects a \
            positive integer (e.g. nb_drones: 4).")

        n = int(nd_match.group("num"))
        if n <= 0:
            raise MapParserError(f"invalid value '{n}' for 'nb_drones'\n\
            \n\t'nb_drones' must be a positive integer greater than zero.")
        return (n)

    @staticmethod
    def _hub_handler(hub_match: re.Match, hub_pattern: re.Pattern
                     ) -> Hub:
        hub: Dict[str, Any] = hub_match.groupdict()

        if not hub["x"] and not hub["y"]:
            raise MapParserError("Missing Hub Coordinate (x, y)")

        elif not hub["y"]:
            raise MapParserError("Missing y axis corrdinate for hub")
        else:
            hub["x"] = int(hub["x"])
            hub["y"] = int(hub["y"])

        if not hub["metadata"]:
            MapParser._metadata_pattern(hub_pattern, hub_match)
        try:
            try:
                hub["metadata"] = MapParser._metadata_parser(
                    "hub", hub["metadata"])
            except ValidationError:
                raise MapParserError(
                    "invalid value\
                    in Metadata for 'max_drones'\n\n\t'max_drones'\
                    must be a positive integer greater than zero.")
            except ValueError:
                raise MapParserError(
                    "invalid value in Metadata for 'max_drones'\n\
                    \n\t'max_drones' must be a valid positive integer")
        except MetaDataParserError as e:
            raise MapParserError(
                f"{e}\n\
                \n\tValid metadata for 'hub': 'color', 'max_drones', 'zone'")

        unexpected_text = re.sub(hub_pattern, '', hub_match.string)
        unexpected_text = re.sub(r"(?:\s+\[.*\])", '', unexpected_text)
        if unexpected_text:
            raise MapParserError(
                "Invalid Line, Additionall Items\n\
                \n\t'hubs' expects exactly: hub: <name> <x> <y> <[metadata]>")
        return Hub(**hub)

    @staticmethod
    def _connections_handler(c_match: re.Match, c_pattern: re.Pattern
                             ) -> Connection:

        connection: Dict[str, Any] = c_match.groupdict()

        if not connection["metadata"]:
            MapParser._metadata_pattern(c_pattern, c_match)
        try:
            try:
                connection["metadata"] = MapParser._metadata_parser(
                    "connection", connection["metadata"])
            except ValidationError:
                raise MapParserError(
                    "invalid value Metadata for 'max_link_capacity'\n\n\t\
                    'max_link_capacity'\
                    must be a positive integer greater than zero.")
            except ValueError:
                raise MapParserError(
                    "invalid value in Metadata for 'max_link_capacity'\n\n\t\
                    'max_link_capacity' must be a valid positive integer")
        except MetaDataParserError as e:
            raise MapParserError(
                f"{e}\n\
                \n\tInvalid metadata for 'connection': 'max_link_capacity'"
            )

        unexpected_text = re.sub(c_pattern, '', c_match.string)
        unexpected_text = re.sub(r"(?:\s+\[.*\])", '', unexpected_text)

        if unexpected_text:
            raise MapParserError(
                "Invalid Line, Additionall Items\n\
                \n\t'hubs' expects exactly: hub: <name> <x> <y> <[metadata]>")
        del connection["sep"]
        del connection["m_content"]

        return Connection(**connection)

    @classmethod
    def from_file(cls, mapfile_path: str | io.TextIOWrapper
                  ) -> "MapParser":
        map_file: io.TextIOWrapper = cls._validated_mapfile(mapfile_path)

        nd_drones: int = -1
        hubs: Dict[str, Hub] = {}
        connection: List[Connection] = []

        file_content = map_file.readlines()

        for line, i in zip(file_content, range(1, len(file_content) + 1)):

            if line.strip().startswith("#") or not len(line.strip()):
                continue

            line = line.split("#")[0].strip()

            nd_pattern = re.compile(r"^nb_drones\s*:\s*(?P<num>(-?\d+)?)$")
            hub_pattern = re.compile(
                r"^(?P<type>start_hub|end_hub|hub):\s*"
                r"(?P<name>\w+)"
                r"(?P<x>\s+-?\d+)?"
                r"(?P<y>\s+-?\d+)?"
                r'(?P<metadata>(\s+\[.*\]))?')

            connection_pattern = re.compile(
                r"^connection\s*:\s+"
                r"(?P<start>\w+)"
                r"(?P<sep>-)"
                r"(?P<end>\w+)"
                r'(?P<metadata>\s+\[(?P<m_content>.*)\])?'
                )

            try:
                if re.match(r"^nb_drones", line):
                    nd_match = nd_pattern.match(line)

                    if nd_match:
                        nd_drones = cls._ndrones_handler(nd_match)
                    else:
                        raise MapParserError(
                            "Invalid Line Format for 'nb_drones'\n\n\t\
                            'nb_drones' expects: nb_drones: <positive_int>")
                elif re.match(r"^(start_hub|end_hub|hub)", line):
                    hub_match = hub_pattern.match(line)

                    if hub_match:
                        hub = cls._hub_handler(hub_match, hub_pattern)
                        hubs[hub.name] = hub
                    else:
                        raise MapParserError(
                            "Invalid Line Format for 'Hub'\n\
                            \n\t'hub' expects: hub: <name> <x> <y> [metadata]"
                        )
                elif re.match(r"^connection", line):
                    connection_match = connection_pattern.match(line)

                    if connection_match:
                        connection.append(
                            cls._connections_handler(
                                connection_match, connection_pattern)
                        )
                    else:
                        raise MapParserError(
                            "Invalid Line Format for 'connection'\n\
                            \n\t'connection' expects: connection:\
                            <hub1_name>-<hub2_name> [metadata]"
                        )
                else:
                    raise MapParserError(
                        "unrecognized syntax\n\
                        \n\tExpected one of: 'nb_drones', 'start_hub',\
                        'hub', 'end_hub', 'connection'"
                    )
            except MapParserError as e:
                raise MapParserError(f"MapParserError: Line {i}: {e}")

        map_file.close()

        return MapParser(
            nd_drones,
            hubs,
            connection
            )
