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
        self.capacity = 0
        self.drones_in = 0
        self.visited: bool = False


class Graph(ABC):
    @staticmethod
    def _create_vertex_from_hubs(data: Dict[str, Hub]) -> List[Vertex]:
        def _set_vertext_type_and_zone(vertex: Vertex) -> None:

            vertex.zone = hub.metadata.zone
            vertex.capacity = hub.metadata.max_drones

            if hub.type == HubType.start_hub:
                vertex.type = VertexType.START
            elif hub.type == HubType.hub:
                vertex.type = VertexType.NORAML
            elif hub.type == HubType.end_hub:
                vertex.type = VertexType.END

        vertex_lst: List[Vertex] = []
        for hub in data.values():
            vertex = Vertex(hub.name)
            _set_vertext_type_and_zone(vertex)

            vertex_lst.append(vertex)

        return vertex_lst


    @staticmethod
    def _create_adjacency_list_graph(
        hubs: Dict[str, Hub],
        connections: List[Connection]) -> Dict[Vertex, List[Vertex]]:

        def _get_vertex_by_name(vertexs: List[Vertex], vertex_name: str) -> Vertex | None:
            for vertex in vertexs:
                if vertex.name == vertex_name:
                    return vertex
            return None

        adjacency_list: Dict[Vertex, List[Vertex]] = {}
        data = Graph._create_vertex_from_hubs(hubs)
        # init empty edges
        for vertex in data:
            if vertex.zone != ZoneTypes.blocked:
                adjacency_list[vertex] = []

        for con in connections:
            start = _get_vertex_by_name(data, con.start)
            end = _get_vertex_by_name(data, con.end)

            if start and end:
                if start.zone != ZoneTypes.blocked and end.zone != ZoneTypes.blocked:
                    adjacency_list[start].append(end)
                    adjacency_list[end].append(start)
                    # if end in adjacency_list:
                    # else:
                    #     adjacency_list[end] = [start]
        return adjacency_list


class PathFinding(ABC):
    @staticmethod
    def _convert_solution_to_str_list(solution: Dict[str, List[Vertex]]) -> List[str]:
        result: List[str] = []

        return result

    @staticmethod
    def _pick_best_path(drone: Drone, graph: Dict[Vertex, List[Vertex]],
                        old_paths: List[List[str]]):

        pass

    @staticmethod
    def _dijkstra_algo(hubs: Dict[str, Hub], connections: List[Connection]) -> List[Vertex]:
        solutions: List[List[Vertex]] = [] ## this is queue
        solution: List[Vertex] = []
        # append list on it
        # sort them using the len key
        # pop the smallest from the queue

        graph = Graph._create_adjacency_list_graph(hubs, connections)

        # create loop throw the drones and each drone pick his path as turns
        # so by default the djikstra algothim pick the short path depend on total of turns need drone to arrive

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
        return solution

    @staticmethod
    def _core(drones: Dict[str, Drone],
              connections: List[Connection],
              hubs: Dict[str, Hub]
              ) -> List[List[str]]:

        graph = Graph._create_adjacency_list_graph(hubs, connections)


        for vertex in graph.keys():
            print("#"*10, vertex.name, "#"*10)
            for neighbor in graph[vertex]:
                print(neighbor.name, end=", ")
            print("\n")



        turn: int = 0
        solution: List[List[str]] = []


        return solution


