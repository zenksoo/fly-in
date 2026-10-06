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
        self.zone: ZoneTypes
        self.visited: bool = False


class Graph(ABC):
    @staticmethod
    def _create_vertex_from_hubs(data: Dict[str, Hub]) -> List[Vertex]:
        def _set_vertext_type_and_zone(vertex: Vertex,
                                       hub_type: Hub
                                       ) -> None:

            vertex.zone = hub.metadata.zone

            if hub.type == HubType.start_hub:
                vertex.type = VertexType.START
            elif hub.type == HubType.hub:
                vertex.type = VertexType.NORAML
            elif hub.type == HubType.end_hub:
                vertex.type = VertexType.END

        vertex_lst: List[Vertex] = []
        for hub in data.values():
            vertex = Vertex(hub.name)
            _set_vertext_type_and_zone(vertex, hub)

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
    def _core(drone: Drone,
              connections: List[Connection],
              hubs: Dict[str, Hub]
              ) -> List[Vertex]:

        solutions: List[List[Vertex]] = [] ## this is queue
        solution: List[Vertex] = []
        # append list on it
        # sort them using the len key
        # pop the smallest from the queue


        vertexs = Graph._create_vertex_from_hubs(hubs)

        graph = Graph._create_adjacency_list_graph(vertexs, connections)

        for vertex in graph.keys():
            if vertex.type == VertexType.START:
                solutions.append([vertex])
                vertex.visited = True
                break

        while True:
            while True:
                small_path: List[Vertex] = solutions.pop()
                print([p.name for p in small_path])
                if small_path[-1].type == VertexType.END:
                    solution = small_path
                    small_path = []
                    break
                elif len(graph[small_path[-1]]) == 0:
                    continue
                else:
                    break

            if not small_path:
                break

            for ne in graph[small_path[-1]]:
                if not ne.visited:
                    solutions.append(small_path + [ne])
                    ne.visited = True

            solutions = sorted(solutions, key=lambda x: len(x))


        test: List[str] = []
        if solution:
            for i in range(len(solution)):
                if (solution[i].type == VertexType.START):
                    continue
                if solution[i].zone == ZoneTypes.restricted:
                    test.append(f"{drone.id}-{solution[i - 1].name}-{solution[i].name}")
                else:
                    test.append(f"{drone.id}-{solution[i].name}")
        print(test)
        return solution
