from Utils import Connection, Drone, Hub, HubType, ZoneTypes
from typing import List, Dict, Tuple
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
        self.max_drones: int
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
    connections: List[Connection]
    vertexs: List[Vertex]
    
    @staticmethod
    def _get_vertex_obj_by_name(vertexs: List[Vertex], target_name: str) -> Vertex | None:
        for vertex in vertexs:
            if vertex.name == target_name:
                return vertex
        return None

    @classmethod
    def _check_vertex_capacity_status(cls, target_vertex: str, current_status: List[str]) -> bool:
        print(current_status)
        drones_in = 0
        for state in current_status:
            if state == target_vertex:
                drones_in += 1

        vertex = cls._get_vertex_obj_by_name(cls.vertexs, target_vertex)

        if vertex:
            return vertex.capacity < drones_in

        return False

    @classmethod
    def _check_connection_capacity_status(cls, target_connection: str, current_status: List[str]) -> bool:
        drones_in = 0
        for state in current_status:
            if state == target_connection:
                print("hhhhhhhhheheheheheh")
                drones_in += 1

        connection: Connection | None = None
        start = target_connection.split("-")[0]
        end = target_connection.split("-")[1]

        for con in cls.connections:
            if con.start == start and con.end == end:
                connection = con
        if connection:
            return connection.metadata.max_link_capacity < drones_in

        return False


    @staticmethod
    def _reset_visited_vertex(vertexs: List[Vertex]) -> None:
        for vertex in vertexs:
            vertex.visited = False


    @classmethod
    def _dijkstra_algo(cls, previews_roads: Dict[str, List[Tuple[int, str]]] , graph: Dict[Vertex, List[Vertex]]) -> List[Tuple[int, str]]:
        # we need to return list of name of each vertex is better than the vertex object

        def _get_vertex_by_name(target_name: str) -> Vertex | None:
            if "-" in target_name:
                target_name = target_name.split("-")[-1]
            for vertex in graph.keys():
                if vertex.name == target_name:
                    return vertex

            return None

        solutions: List[List[Tuple[int, str]]] = [] ## this is queue
        solution: List[Tuple[int, str]] = []
        # append list on it
        # sort them using the len key
        # pop the smallest from the queue

        # create loop throw the drones and each drone pick his path as turns
        # so by default the djikstra algothim pick the short path depend on total of turns need drone to arrive

        for vertex in graph.keys():
            if vertex.type == VertexType.START:
                solutions.append([(0, vertex.name)])
                vertex.visited = True
                break

        while True:
            while True:
                small_path: List[Tuple[int, str]] = solutions.pop(0)
                last_vertex: Vertex | None = _get_vertex_by_name(small_path[-1][1])
                if not last_vertex:
                    raise ValueError(f"There is no Vertex object with name `{small_path[-1][1]}`")

                if last_vertex.type == VertexType.END:
                    solution = small_path
                    small_path = []
                    break
                # if there is no neighbors for the vertex, mean uncomplated route so remove them
                elif len(graph[last_vertex]) == 0:
                    continue
                else:
                    break

            if not small_path:
                break

            curr_turn = small_path[-1][0] + 1
            for ne in graph[last_vertex]:

                if not ne.visited:
                    tmp_path = small_path
                    # if ne.zone == ZoneTypes.restricted:
                    #     curr_turn_actions = [e[1] for s in previews_roads.values() for e in s if e[0] == curr_turn]
                    #     if (cls._check_connection_capacity_status(curr_turn, f"{last_vertex.name}-{ne.name}", curr_turn_actions)):
                    #         tmp_path += [(curr_turn, f"{last_vertex.name}-{ne.name}")]
                    #     else:
                    #         tmp_path += [(curr_turn, f"{small_path[-1][1]}")]

                    #     solutions.append(tmp_path + [(curr_turn + 1, ne.name)])
                    # else:
                    ne.visited = True
                    if previews_roads:
                        curr_turn_actions = [e[1] for s in previews_roads.values() for e in s if e[0] == curr_turn]
                        if cls._check_vertex_capacity_status(ne.name, curr_turn_actions):
                            solutions.append(tmp_path + [(curr_turn, ne.name)])
                        else:
                            solutions.append(tmp_path + [(curr_turn, small_path[-1][1])])
                            ne.visited = False
                    else:
                        solutions.append(tmp_path + [(curr_turn, ne.name)])



            solutions = sorted(solutions, key=lambda x: len(x))
        return solution

    # @staticmethod
    # def  _pick_drone_route(previes_routes: Dict[str, List[Vertex]],
    #                       grap: Dict[Vertex, List[Vertex]]
    #                       ) -> List[Tuple[int, str]]:
    #     route: List[Tuple[int, str]] = []

    #     if not previes_routes:
    #         # route =
    #     else:
    #         # to check the best road for current drone
    #         # i need to track state of connection and vertex on each turn
    #         # to see if i can move the drone to the vertex on the way or no ?
    #         # or mke them wait until others arrive




    #         pass

    #     return route

    @classmethod
    def _core(cls, drones: Dict[str, Drone],
              connections: List[Connection],
              hubs: Dict[str, Hub]
              ) -> List[List[str]]:

        cls.connections = connections

        graph = Graph._create_adjacency_list_graph(hubs, connections)

        cls.vertexs = list(graph.keys())

        drones_solution: Dict[str, List[Tuple[int, str]]] = {}

        for drone_id in drones.keys():
            PathFinding._reset_visited_vertex(list(graph.keys()))
            drones_solution[drone_id] = PathFinding._dijkstra_algo(drones_solution, graph)
            print("#"*15, drone_id, "#"*15)
            for turn, vertex_name in drones_solution[drone_id]:
                print("turn   : ", turn)
                print("vertex : ", vertex_name)

            print("\n\n")


        turn: int = 1
        solution: List[List[str]] = []

        while True:
            if all([e[0] != turn for s in drones_solution.values() for e in s]):
                break
            turn_solution: List[str] = []
            for drone_id in drones_solution.keys():
                for e in drones_solution[drone_id]:
                    if e[0] == turn:
                        turn_solution.append(f"{drone_id}-{e[1]}")
                    elif e[0] > turn:
                        break

            solution.append(turn_solution)
            turn += 1


        return solution


