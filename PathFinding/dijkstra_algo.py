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
    def _create_adjacency_list_graph(
        data: List[Vertex],
        connections: List[Connection]) -> Dict[Vertex, List[Vertex]]:

        def _get_vertex_by_name(vertexs: List[Vertex], vertex_name: str) -> Vertex | None:
            for vertex in vertexs:
                if vertex.name == vertex_name:
                    return vertex
            return None

        adjacency_list: Dict[Vertex, List[Vertex]] = {}
        # init empty edges
        for vertex in data:
            adjacency_list[vertex] = []

        for con in connections:
            start = _get_vertex_by_name(data, con.start)
            end = _get_vertex_by_name(data, con.end)

            if start and end:
                if start in adjacency_list:
                    adjacency_list[start].append(end)
                else:
                    adjacency_list[start] = [end]

                if end in adjacency_list:
                    adjacency_list[end].append(start)
                else:
                    adjacency_list[end] = [start]
        return adjacency_list


class PathFinding(ABC):
    @staticmethod
    def _core(connections: List[Connection],
              hubs: Dict[str, Hub]
              ) -> List[List[str]]:

        solution: List[List[str]] = []

        data = GraphTheory._create_vertex_from_hubs(hubs)

        graph = GraphTheory._create_adjacency_list_graph(data, connections)

        for e in graph.keys():
            print(e.name, e.type)
            for ne in graph[e]:
                print("     ", ne.name, ne.type)

        return solution
