from typing import List


class WCfgParser:
    pass


class MapParser:
    def __init__(self, map_file_path: str) -> None:
        self.map_file = open(map_file_path, 'r')

    def parse(self) -> None:
        data = {
            "nb_drones": 0,
            "hubs": {},
            "connections": []
        }
        content_lines = self.map_file.readlines()
        self.map_file.close()

        for line in content_lines:
            line = line.strip()
            if (line.startswith("#") or not len(line)):
                continue
            line = line.split(":")
            if line[0] == "start_hub":
                data["hubs"]["type"] = "start_hub"
                data["hubs"]["name"] = 
            print(line)
            # if line.startswith("nb_drones"):
            #     data["nb_drones"] = int(line.split(":")[1])


        print(data)

