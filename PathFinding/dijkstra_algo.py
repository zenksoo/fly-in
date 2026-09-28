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

        def _get_vertex_by_name(vertexs: List[Vertex], vertex_name: str) -> Vertex | None:
            for vertex in vertexs:
                if vertex.name == vertex_name:
                    return vertex

            return None

        edges_lst: Dict[Vertex, List[Vertex]] = {}
        # init empty edges
        for vertex in data:
            edges_lst[vertex] = []

        for con in connections:
            start = _get_vertex_by_name(data, con.start)
            end = _get_vertex_by_name(data, con.end)

            if start and end:
                if start in edges_lst:
                    edges_lst[start].append(end)
                else:
                    edges_lst[start] = [end]

                if end in edges_lst:
                    edges_lst[end].append(start)
                else:
                    edges_lst[end] = [start]


        return edges_lst
    @staticmethod
    def _create_graph(vertexs: List[Vertex], edges: Dict[Vertex, List[Vertex]]) -> List[List[int]]:
        def _init_empty_graph(vertexs: List[Vertex]) -> List[List[int]]:
            graph: List[List[int]] = []
            for column in range(len(vertexs)):
                graph.append([])
                for row in range(len(vertexs)):
                    graph[column].append(0)


            return graph



        def _get_vertex_idx(vertexs: List[Vertex], target_vertex: Vertex) -> int:
            for i in range(len(vertexs)):
                if (vertexs[i] == target_vertex):
                    return i
            return -1

        graph: List[List[int]] = _init_empty_graph(vertexs)




        return graph

class PathFinding:
    # def __new__(cls) -> Self:
    #     raise RuntimeError("u can't create object from this class")


    def __init__(self) -> None:

        pass



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

            return result


        # for con in connections:
        #     print(con.start, con.end)

        hubs_neighbors = _get_hub_neighbors(hubs, connections)

        # for key in hubs_neighbors.keys():
        #     print(key)
        #     for vertex in hubs_neighbors[key]:
        #         print("     >> ", vertex.name, vertex.type)

        data = GraphTheory._create_vertex_from_hubs(hubs)

        edges = GraphTheory._generate_vertex_edges_from_connections(data, connections)

        graph = GraphTheory._create_graph(data, edges)

        for y in graph:
            for x in y:
                print(f" {x} ", end="")
            print("")


        # for e in edges.keys():
        #     print(e.name, e.type)
        #     for ne in edges[e]:
        #         print("     ", ne.name, ne.type)



        # for d in data:
        #     print(d.name, d.type)



        return solution

