from typing import List
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

        return map_file

    @staticmethod
    def parse(mapfile_path: str | io.TextIOWrapper) -> None:
        map_file: io.TextIOWrapper = MapParser._validated_mapfile(mapfile_path)
        if isinstance(mapfile_path, str):
            map_file = open(mapfile_path, 'r')
        elif isinstance(mapfile_path, io.TextIOWrapper):
            map_file = mapfile_path
        def _ndrones_handler(match: re.Match) -> None:
            pass

        def _hub_handler(match: re.Match) -> None:
            pass

        def _connections_handler( match: re.Match) -> None:
            pass


        # for line in content_lines:
        #     if line.startswith("#") or not len(line.strip()):
        #         continue
        #     line = line.split("#")[0].strip()
        #     res = re.match("hub", line)
        #     # if res:
        #     #     ndrones_parse(res)

        #     # if (line.startswith("#") or not len(line)):
            #     continue
