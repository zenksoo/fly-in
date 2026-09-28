from Utils import Connection, Drone, Hub, HubType, ZoneTypes
from typing import List, Dict
from enum import Enum
from abc import ABC

class VertexType(str, Enum):
    START = "start"
    NORAML = "normal"
    END = "end"


class Vertex:
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.type: VertexType
        self.visited: bool = False


class GraphTheory(ABC):
    @staticmethod
    def _create_vertex_from_hubs(data: Dict[str, Hub]) -> List[Vertex]:
        def _set_vertext_type(vertex: Vertex, hub_type: HubType) -> None:
            if hub_type == HubType.start_hub:
                vertex.type = VertexType.START
            elif hub_type == HubType.hub:
                vertex.type = VertexType.NORAML
            elif hub_type == HubType.end_hub:
                vertex.type = VertexType.END

        vertex_lst: List[Vertex] = []
        for hub in data.values():
            vertex = Vertex(hub.name)
            _set_vertext_type(vertex, hub.type)

            vertex_lst.append(vertex)

        return vertex_lst


    @staticmethod
    def _generate_vertex_edges_from_connections(
        data: List[Vertex],
        connections: List[Connection]) -> Dict[Vertex, List[Vertex]]:

        edges_lst: Dict[Vertex, List[Vertex]] = {}

        # init empty edges
        for vertex in data:
            edges_lst[vertex] = []

        for vertex in data:

            print(vertex.name)

        return edges_lst


class PathFinding:
    # def __new__(cls) -> Self:
    #     raise RuntimeError("u can't create object from this class")


    def __init__(self) -> None:

        pass
    @staticmethod
    def _create_graph(data, connections: List[Connection]) -> List[List[int]]:
        graph: List[List[int]] = []



        return graph


    @staticmethod
    def _astart_algorithm(connections: List[Connection], hubs: Dict[str, Hub]) -> List[List[str]]:
        solution: List[List[str]] = []

        def _get_hub_neighbors(hubs: Dict[str, Hub],
                               connections: List[Connection]
                               ) -> Dict[str, List[Vertex]]:
            # it return dictionry of hub name and his neighbors hubs in list
            result: Dict[str, List[Vertex]] = {}

            def _set_vertext_type(vertex: Vertex, hub_type: HubType) -> None:
                if hub_type == HubType.start_hub:
                    vertex.type = VertexType.START
                elif hub_type == HubType.hub:
                    vertex.type = VertexType.NORAML
                elif hub_type == HubType.end_hub:
                    vertex.type = VertexType.END

            for con in connections:
                start_hub = con.start
                end_hub = con.end

                if start_hub in result.keys():
                    result[start_hub].append(Vertex(end_hub))
                else:
                    result[start_hub] = [Vertex(end_hub)]

                _set_vertext_type(result[start_hub][-1], hubs[end_hub].type)

                if end_hub in result.keys():
                    result[end_hub].append(Vertex(start_hub))
                else:
                    result[end_hub] = [Vertex(start_hub)]

                _set_vertext_type(result[end_hub][-1], hubs[start_hub].type)
                print(hubs[start_hub].metadata.zone)

            return result


        # for con in connections:
        #     print(con.start, con.end)

        hubs_neighbors = _get_hub_neighbors(hubs, connections)

        for key in hubs_neighbors.keys():
            print(key)
            for vertex in hubs_neighbors[key]:
                print("     >> ", vertex.name, vertex.type)

        data = GraphTheory._create_vertex_from_hubs(hubs)

        edges = GraphTheory._generate_vertex_edges_from_connections(data, connections)



        for d in data:
            print(d.name, d.type)



        return solution

