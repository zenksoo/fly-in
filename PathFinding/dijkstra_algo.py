from Utils import Connection, Drone, Hub, HubType, ZoneTypes
from typing import List, Dict, Tuple
from enum import Enum
from abc import ABC


class VertexType(str, Enum):
    START = "start"
    NORMAL = "normal"
    END = "end"


class Vertex:
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.type: VertexType
        self.zone: ZoneTypes
        self.max_drones: int
        self.capacity = 0
        self.drones_in = 0
        self.visited: bool = False


class GraphBuilder(ABC):
    @staticmethod
    def build_vertices_from_hubs(data: Dict[str, Hub]) -> List[Vertex]:
        def _apply_hub_settings(vertex: Vertex) -> None:

            vertex.zone = hub.metadata.zone
            vertex.capacity = hub.metadata.max_drones


            if hub.type == HubType.start_hub:
                vertex.type = VertexType.START
            elif hub.type == HubType.hub:
                vertex.type = VertexType.NORMAL
            elif hub.type == HubType.end_hub:
                vertex.type = VertexType.END

        vertex_lst: List[Vertex] = []
        for hub in data.values():
            vertex = Vertex(hub.name)
            _apply_hub_settings(vertex)

            vertex_lst.append(vertex)

        return vertex_lst


    @staticmethod
    def build_adjacency_list(
        hubs: Dict[str, Hub],
        connections: List[Connection]) -> Dict[Vertex, List[Vertex]]:

        def _get_vertex_by_name(vertexs: List[Vertex], vertex_name: str) -> Vertex | None:
            for vertex in vertexs:
                if vertex.name == vertex_name:
                    return vertex
            return None

        adjacency_list: Dict[Vertex, List[Vertex]] = {}
        data = GraphBuilder.build_vertices_from_hubs(hubs)
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
    connections: List[Connection]
    vertexs: List[Vertex]

    @classmethod
    def _find_vertex(cls, target_name: str) -> Vertex | None:
        for vertex in cls.vertexs:
            if vertex.name == target_name:
                return vertex
        return None

    @classmethod
    def _can_enter_vertex(cls, source_vertex: Vertex, target_name: str, occupied_positions: List[str]) -> bool:
        occupant_count = 0
        connection: Connection | None = None
        for con in cls.connections:
            if con.start == source_vertex.name and con.end == target_name:
                connection = con

        for position in occupied_positions:
            if position == target_name:
                occupant_count += 1

        vertex = cls._find_vertex(target_name)

        if vertex and connection:
            return vertex.capacity > occupant_count and connection.metadata.max_link_capacity > occupant_count

        return False

    @classmethod
    def _can_use_connection(cls, connection_label: str, current_status: List[str]) -> bool:
        occupant_count = 0
        for position in current_status:
            if position == connection_label:
                occupant_count += 1

        connection: Connection | None = None
        start = connection_label.split("-")[0]
        end = connection_label.split("-")[1]

        for con in cls.connections:
            if con.start == start and con.end == end:
                connection = con

        if connection:
            return connection.metadata.max_link_capacity > occupant_count

        return False

    @staticmethod
    def _reset_visited_flags(vertexs: List[Vertex]) -> None:
        for vertex in vertexs:
            vertex.visited = False


    @classmethod
    def _find_route_for_drone(cls, planned_routes: Dict[str, List[Tuple[int, str]]] , graph: Dict[Vertex, List[Vertex]]) -> List[Tuple[int, str]]:
        route_queue: List[List[Tuple[int, str]]] = [] ## this is queue
        best_route: List[Tuple[int, str]] = []
        # append list on it
        # sort them using the len key
        # pop the smallest from the queue

        # create loop throw the drones and each drone pick his path as turns
        # so by default the djikstra algothim pick the short path depend on total of turns need drone to arrive

        for vertex in graph.keys():
            if vertex.type == VertexType.START:
                route_queue.append([(0, vertex.name)])
                vertex.visited = True
                break

        while True:
            while True:
                current_route: List[Tuple[int, str]] = route_queue.pop(0)
                if "-" in current_route[-1][1]:
                    current_vertex: Vertex | None = cls._find_vertex(current_route[-1][1].split("-")[1])
                else:
                    current_vertex: Vertex | None = cls._find_vertex(current_route[-1][1])
                if not current_vertex:
                    raise ValueError(f"There is no Vertex object with name `{current_route[-1][1]}`")

                if current_vertex.type == VertexType.END:
                    best_route = current_route
                    current_route = []
                    break
                # if there is no neighbors for the vertex, mean uncomplated route so remove them
                elif len(graph[current_vertex]) == 0:
                    continue
                else:
                    break

            if not current_route:
                break

            next_turn = current_route[-1][0] + 1
            reference_turn = -1
            for i in range(-1, -len(current_route), -1):
                if current_route[i][1] == current_route[i - 1]:
                    reference_turn = len(current_route) + i

            if reference_turn == -1:
                reference_turn = next_turn
            print("\n\n","#"*20, "\n\n")
            print(current_route)
            for neighbor in graph[current_vertex]:
                print("the end of path: ", current_vertex.name, neighbor.name)
                if not neighbor.visited:
                    tmp_route = current_route
                    occupied_positions = [e[1] for s in planned_routes.values() for e in s if e[0] == reference_turn]
                    if neighbor.zone == ZoneTypes.restricted:
                        if (cls._can_use_connection(f"{current_vertex.name}-{neighbor.name}", occupied_positions)):
                            tmp_route += [(next_turn, f"{current_vertex.name}-{neighbor.name}")]
                            route_queue.append(tmp_route + [(next_turn + 1, neighbor.name)])
                        else:
                            route_queue.append(tmp_route + [(next_turn, current_route[-1][1])])
                    else:
                        neighbor.visited = True
                        if planned_routes:
                            if cls._can_enter_vertex(current_vertex, neighbor.name, occupied_positions):
                                route_queue.append(tmp_route + [(next_turn, neighbor.name)])
                            else:
                                route_queue.append(tmp_route + [(next_turn, current_route[-1][1])])
                                neighbor.visited = False
                        else:
                            route_queue.append(tmp_route + [(next_turn, neighbor.name)])

            route_queue = sorted(route_queue, key=lambda x: len(x))
        return best_route


    @classmethod
    def plan_all_drones(cls, drones: Dict[str, Drone],
              connections: List[Connection],
              hubs: Dict[str, Hub]
              ) -> List[List[str]]:

        cls.connections = connections

        graph = GraphBuilder.build_adjacency_list(hubs, connections)

        cls.vertexs = list(graph.keys())

        routes_by_drone: Dict[str, List[Tuple[int, str]]] = {}

        for drone_id in drones.keys():
            PathFinding._reset_visited_flags(cls.vertexs)
            routes_by_drone[drone_id] = PathFinding._find_route_for_drone(routes_by_drone, graph)
            print("#"*15, drone_id, "#"*15)
            for turn_number, vertex_name in routes_by_drone[drone_id]:
                print("turn   : ", turn_number)
                print("vertex : ", vertex_name)

            print("\n\n")


        turn_number: int = 1
        moves_per_turn: List[List[str]] = []

        # remove repeated instruction from the solution
        for drone_id in routes_by_drone.keys():
            for i in range(len(routes_by_drone[drone_id])):
                j = i + 1
                while j < len(routes_by_drone[drone_id]) and routes_by_drone[drone_id][i][1] == routes_by_drone[drone_id][j][1]:
                    routes_by_drone[drone_id].remove(routes_by_drone[drone_id][j])
                    j += 1

        while True:
            if all([step[0] != turn_number for route in routes_by_drone.values() for step in route]):
                break
            turn_moves: List[str] = []
            for drone_id in routes_by_drone.keys():
                for step in routes_by_drone[drone_id]:
                    if step[0] == turn_number:
                        turn_moves.append(f"{drone_id}-{step[1]}")
                    elif step[0] > turn_number:
                        break

            moves_per_turn.append(turn_moves)
            turn_number += 1


        return moves_per_turn


