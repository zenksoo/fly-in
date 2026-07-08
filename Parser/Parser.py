from typing import List


class WCfgParser:
    pass

import re

line = "nb_drones: 23"

thematch = re.match(
    r"", line)

class MapParser:
    def __init__(self, map_file_path: str) -> None:
        self.map_file = open(map_file_path, 'r')

    def parse(self) -> None:
        # data = {
        #     "nb_drones": 0,
        #     "hubs": {},
        #     "connections": []
        # }
        content_lines = self.map_file.readlines()
        self.map_file.close()

        for line in content_lines:
            if line.startswith("#") or not len(line.strip()):
                continue
            line = line.split("#")[0].strip()
            print(line)
            # if (line.startswith("#") or not len(line)):
            #     continue

        print(data)

