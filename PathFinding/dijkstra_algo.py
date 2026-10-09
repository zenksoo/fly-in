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
    def _reset_visited_vertex(vertexs: List[Vertex]) -> None:
        for vertex in vertexs:
            vertex.visited = False

    @staticmethod
    def _format_the_path(path: List[Vertex], drone_id: str) -> List[str]:
        result: List[str] = []

        for i in range(len(path)):
            if path[i].zone == ZoneTypes.restricted:
                result.append(f"{drone_id}-{path[i - 1].name}-{path[i].name}")
                result.append(f"{drone_id}-{path[i].name}")
            else:
                result.append(f"{drone_id}-{path[i].name}")

        return result

    @staticmethod
    def _dijkstra_algo(graph: Dict[Vertex, List[Vertex]]) -> List[Vertex]:
        solutions: List[List[Vertex]] = [] ## this is queue
        solution: List[Vertex] = []
        # append list on it
        # sort them using the len key
        # pop the smallest from the queue

        # create loop throw the drones and each drone pick his path as turns
        # so by default the djikstra algothim pick the short path depend on total of turns need drone to arrive

        for vertex in graph.keys():
            if vertex.type == VertexType.START:
                solutions.append([vertex])
                vertex.visited = True
                break

        while True:
            while True:
                small_path: List[Vertex] = solutions.pop(0)
                if small_path[-1].type == VertexType.END:
                    solution = small_path
                    small_path = []
                    break
                # if there is no neighbors for the vertex, mean uncomplated route so remove them
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

            solutions = sorted(solutions,
                               key=(
                                   lambda x: sum(
                                       [2 if e.zone == ZoneTypes.restricted else 1 for e in x]
                                       )
                                   ))
        return solution

    @staticmethod
    def  _pick_drone_route(previes_routes: Dict[str, List[Vertex]],
                          grap: Dict[Vertex, List[Vertex]]
                          ) -> List[Vertex]:
        route: List[Vertex] = []

        if not previes_routes:
            route = PathFinding._dijkstra_algo(grap)
        else:
            pass

        return route

    @staticmethod
    def _core(drones: Dict[str, Drone],
              connections: List[Connection],
              hubs: Dict[str, Hub]
              ) -> List[List[str]]:

        graph = Graph._create_adjacency_list_graph(hubs, connections)

        # short_path = PathFinding._dijkstra_algo(graph)

        # print("#" * 10, " shortest path is ", "#"*10)
        # for vertex in short_path:
        #     print(vertex.name, end=", ")
        # print("\n\n")

        drones_solution: Dict[str, List[Vertex]] = {}

        for drone_id in drones.keys():
            PathFinding._reset_visited_vertex(list(graph.keys()))
            drones_solution[drone_id] = PathFinding._pick_drone_route(drones_solution, graph)
            print(PathFinding._format_the_path(drones_solution[drone_id], drone_id))
            break

        turn: int = 0
        solution: List[List[str]] = []

        return solution


