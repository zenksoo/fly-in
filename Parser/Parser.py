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
    def _metadata_parser(metadata_for: str, data: str
                         ) -> HubMetaData | ConnectionMetadata | None:
        if not data:
            if metadata_for == "hub":
                return HubMetaData()
            elif metadata_for == "connection":
                return ConnectionMetadata()

        data = re.sub(r"\s+", ' ', data)

        registred_metadata_for_hub = ['color', 'max_drones',
                                      'zone']
        registred_metadata_for_connection = ['max_link_capacity']
        metadata_dict: Dict[str, Any] = {}

        for property in data.split(" "):
            if ("=" not in property or (len(property.split("=")) > 2) or
               len(property.split("=")[1]) == 0):
                raise MapParserError(
                    f"invalid properties syntax '{property}'\
                    in meatadata\n\n\tProperties must follow \
                    'key=value' format: [color=green]"
                )
            key, val = property.split("=")
            if ((metadata_for == "hub"
               and key not in registred_metadata_for_hub) or
               metadata_for == "connection"
               and key not in registred_metadata_for_connection):
                raise MetaDataParserError(
                    f"unknown metadata property '{key}'\n")
            if key == "zone":
                try:
                    metadata_dict[key] = ZoneTypes[val]
                except KeyError:
                    raise MapParserError(f"invalide zone type '{val}'")
            elif key == "color":
                try:
                    metadata_dict[key] = Colors[val]
                except KeyError:
                    raise MapParserError(f"unregistred color '{val}'")
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

        hub["x"] = int(hub["x"])
        hub["y"] = int(hub["y"])

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
                f"{e.msg}\n\
                \n\tValid metadata for 'hub': 'color', 'max_drones', 'zone'")
        return Hub(**hub)

    @staticmethod
    def _connections_handler(c_match: re.Match, c_pattern: re.Pattern
                             ) -> Connection:

        connection: Dict[str, Any] = c_match.groupdict()
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
                f"{e.msg}\n\
                \n\tvalid metadata for 'connection': 'max_link_capacity'"
            )
        return Connection(**connection)

    @classmethod
    def from_file(cls, file: str | io.TextIOWrapper
                  ) -> "MapParser":
        map_file: io.TextIOWrapper = cls._validated_mapfile(file)

        nd_drones: int = -1
        hubs: Dict[str, Hub] = {}
        connections: List[Connection] = []

        file_content = map_file.readlines()

        for line, i in zip(file_content, range(1, len(file_content) + 1)):

            if line.strip().startswith("#") or not len(line.strip()):
                continue

            line = line.split("#")[0].strip()

            nd_pattern = re.compile(r"^nb_drones\s*:\s*(?P<num>(-?\d+)?)$")

            hub_pattern = re.compile(
                r"^(?P<type>start_hub|end_hub|hub):\s*"
                r"(?P<name>\S+)\s+"
                r"(?P<x>-?\d+)\s+"
                r"(?P<y>-?\d+)"
                r"(?:\s+\[(?P<metadata>[^\]]*)\])?"
                r"\s*$"
            )

            connection_pattern = re.compile(
                r"^connection\s*:\s+"
                r"(?P<start>[^\s-]+)"
                r"-"
                r"(?P<end>[^\s-]+)"
                r"(?:\s+\[(?P<metadata>[^\]]*)\])?"
                r"\s*$"
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
                    if nd_drones == -1:
                        raise MapParserError(
                            "The first line must define the number of drones")
                    hub_match = hub_pattern.match(line)

                    if hub_match:
                        hub = cls._hub_handler(hub_match, hub_pattern)
                        if (hub.name in hubs.keys()):
                            raise MapParserError(
                                "Doublicate Hub Name"
                            )
                        elif ('-' in hub.name):
                            raise MapParserError(
                                "invalid hub name the name must not include -"
                            )
                        hubs[hub.name] = hub
                    else:
                        raise MapParserError(
                            "Invalid Line Format for 'Hub'\n\
                            \n\t'hub' expects: hub: <name> <x> <y> [metadata]"
                        )
                elif re.match(r"^connection", line):
                    connection_match = connection_pattern.match(line)

                    if connection_match:
                        connection = cls._connections_handler(
                            connection_match, connection_pattern)

                        if connection.start not in hubs.keys():
                            raise MapParserError(
                                f"unregistered hub '{connection.start}'\n\
                                \n\tHub must be declared before it can be \
                                used in a connection"
                            )
                        elif connection.end not in hubs.keys():
                            raise MapParserError(
                                f"unregistered hub '{connection.end}'\n\
                                \n\tHub must be declared before it can be \
                                used in a connection"
                            )
                        elif (connection.start == connection.end):
                            raise MapParserError(
                                f"invalid connection \
                                '{connection.start}-{connection.end}'\n\
                                \n\tA hub cannot be connected to itself."
                            )
                        elif (([connection.start, connection.end] in
                              [[c.start, c.end] for c in connections]) or
                              ([connection.end, connection.start] in
                              [[c.start, c.end] for c in connections])):
                            raise MapParserError("tzzzz a w9")
                        connections.append(connection)
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
                raise MapParserError(f"Line {i}: {e.msg}")

        map_file.close()

        return MapParser(
            nd_drones,
            hubs,
            connections
            )
