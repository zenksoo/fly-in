from Utils import Connection, Drone, Hub, HubType
from typing import List, Dict
from enum import Enum

class VertexType(str, Enum):
    START = "start_hub"
    NORAML = "hub"
    END = "end_hub"


class Vertex:
    def __init__(self, name: str, type: VertexType) -> None:
        self.name: str = name
        self.type: VertexType = type
        self.visited: bool = False

class PathFinding:
    # def __new__(cls) -> Self:
    #     raise RuntimeError("u can't create object from this class")

    def __init__(self) -> None:

        pass


    @staticmethod
    def _astart_algorithm(connections: List[Connection], hubs: Dict[str, Hub]) -> List[List[str]]:
        solution: List[List[str]] = []

        def _get_hub_neighbors(hubs: Dict[str, Hub], connections: List[Connection]) -> Dict[str, List[Vertex]]:
            # it return dictionry of hub name and his neighbors hubs in list
            result: Dict[str, List[Vertex]] = {}

            for con in connections:
                start_hub = con.start
                end_hub = con.end

                start_vertex_type = VertexType(hubs[start_hub].type)
                end_vertext_type = VertexType(hubs[end_hub].type)
                print(start_vertex_type, end_vertext_type)


                if start_hub in result.keys():
                    if (end_hub not in result[start_hub]):
                        result[start_hub].append(Vertex(hubs[end_hub].name, end_vertext_type))
                else:
                    if (hubs[start_hub].type != HubType.end_hub):
                        result[start_hub] = [Vertex(hubs[end_hub].name, end_vertext_type)]

                if end_hub in result.keys():
                    if (start_hub not in result[end_hub]):
                        result[end_hub].append(Vertex(hubs[start_hub].name, start_vertex_type))
                else:
                    if (hubs[end_hub].type != HubType.end_hub):
                        result[end_hub] = [Vertex(hubs[start_hub].name, start_vertex_type)]
            return result


        # for con in connections:
        #     print(con.start, con.end)

        hubs_neighbors = _get_hub_neighbors(hubs, connections)

        for key in hubs_neighbors.keys():
            print(key, [h.type for h in hubs_neighbors[key]])


        return solution

