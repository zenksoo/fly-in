from Utils import Connection, Drone, Hub, HubType, ZoneTypes
from typing import List, Dict, Tuple
from abc import ABC
from heapq import heappush, heappop
from functools import total_ordering
from CExceptions import InvalidMap


class GraphBuilder(ABC):
    @staticmethod
    def build_adjacency_list(hubs: Dict[str, Hub],
                             connections: List[Connection]
                             ) -> Dict[str, List[Hub]]:
        """
            Build an adjacency list representation of the graph based on hubs and connections.

            Args:
                hubs (Dict[str, Hub]): A dictionary of hubs with hub names as keys.
                connections (List[Connection]): A list of connections between hubs.

            Returns:
                Dict[str, List[Hub]]: An adjacency list representation of the graph.
        """

        def _get_hub_by_name(hubs: List[Hub], hub_name: str) -> Hub | None:
            for hub in hubs:
                if hub.name == hub_name:
                    return hub
            return None

        adjacency_list: Dict[str, List[Hub]] = {}
        # init empty edges
        for hub in hubs.values():
            if hub.metadata.zone != ZoneTypes.blocked:
                adjacency_list[hub.name] = []

        for con in connections:
            start = _get_hub_by_name(list(hubs.values()), con.start)
            end = _get_hub_by_name(list(hubs.values()), con.end)

            if start and end:
                if (start.metadata.zone != ZoneTypes.blocked and
                        end.metadata.zone != ZoneTypes.blocked):
                    adjacency_list[start.name].append(end)
                    adjacency_list[end.name].append(start)

        return adjacency_list


@total_ordering
class Step:
    """
        Class representing a step in the pathfinding process.
    """
    def __init__(self, turn: int = 0) -> None:
        self.turn = turn
        # self.dest_name: str = name
        self.origin: Hub
        self.dest: Hub

    def __lt__(self, other: "Step") -> bool:
        """
            Compare two Step instances based on their destination hub's zone and type.

            Args:
                other (Step): The other Step instance to compare with.

            Returns:
                bool: True if this Step instance is considered "less than" the other, False otherwise.
        """

        if (self.dest.metadata.zone == ZoneTypes.priority):
            return True
        elif (other.dest.metadata.zone == ZoneTypes.priority):
            return False
        if self.dest.type == HubType.end_hub:
            return True
        elif other.dest.type == HubType.end_hub:
            return False

        return True


class PathFinding(ABC):
    """
        Abstract base class for pathfinding algorithms.
    """

    connections: List[Connection]
    hubs: List[Hub] = []
    planned_routes: Dict[str, List[Step]] = {}
    turn_changes_register: Dict[str, List[Tuple[str, str]]] = {}

    @classmethod
    def _update_turns_changes(cls, steps: List[Step]) -> None:
        """
            Update the turn changes register with the given steps.

            Args:
                steps (List[Step]): A list of Step instances to update the register with.
        """

        for step in steps:
            if (step.dest.metadata.zone == ZoneTypes.restricted and
                    step.dest != step.origin):
                key = f"turn_{step.turn - 1}"
                dest_label = f"{step.origin.name}-{step.dest.name}"
                if (cls.turn_changes_register.get(key)):
                    cls.turn_changes_register[key].append(
                        (step.origin.name, dest_label)
                    )
                else:
                    cls.turn_changes_register[key] = [
                        (step.origin.name, dest_label)]
            key = f"turn_{step.turn}"
            if (cls.turn_changes_register.get(key)):
                cls.turn_changes_register[key].append(
                    (step.origin.name, step.dest.name)
                )
            else:
                cls.turn_changes_register[key] = [
                    (step.origin.name, step.dest.name)
                ]

    @classmethod
    def _get_turn_changes(cls, turn: int) -> List[Tuple[str, str]]:
        """
            Get the list of changes for a specific turn from the turn changes register.

            Args:
                turn (int): The turn number to get changes for.

            Returns:
                List[Tuple[str, str]]: A list of tuples representing the changes for the specified turn.
        """
        key = f"turn_{turn}"
        if (cls.turn_changes_register.get(key)):
            return cls.turn_changes_register[key]
        return []

    @classmethod
    def _find_hub(cls, target_name: str) -> Hub | None:
        """
            Find a hub by its name in the list of hubs.

            Args:
                target_name (str): The name of the hub to find.

            Returns:
                Hub | None: The hub if found, None otherwise.
        """
        for hub in cls.hubs:
            if hub.name == target_name:
                return hub
        return None

    @classmethod
    def can_enter_hub(cls, source: Hub,
                      dest: Hub,
                      occupied_positions: List[Tuple[str, str]]
                      ) -> bool:
        """
            Check if a drone can enter a destination hub from a source hub based on the current occupied
            positions and the hub's capacity.

            Args:
                source (Hub): The source hub.
                dest (Hub): The destination hub.
                occupied_positions (List[Tuple[str, str]]): A list of tuples representing the current occupied positions.

            Returns:
                bool: True if the drone can enter the destination hub, False otherwise.
        """
        occupant_count = 0
        occupant_con_count = 0
        connection: Connection | None = None
        for con in cls.connections:
            if ((con.start == source.name and con.end == dest.name) or
                    (con.start == dest.name and con.end == source.name)):
                connection = con

        for origin, position in occupied_positions:
            if (connection and
                    ((connection.start == origin and
                      connection.end == position) or
                     (connection.start == position and
                      connection.end == origin))):
                occupant_con_count += 1
            if position == dest.name:
                occupant_count += 1

        if connection:
            return (
                connection.metadata.max_link_capacity > occupant_con_count and
                dest.metadata.max_drones > occupant_count
            )

        return False

    @classmethod
    def can_use_connection(cls, source: Hub,
                           dest: Hub,
                           occupied_positions: List[Tuple[str, str]]
                           ) -> bool:
        """
            Check if a drone can use a connection between two hubs based on the current occupied positions
            and the connection's capacity.

            Args:
                source (Hub): The source hub.
                dest (Hub): The destination hub.
                occupied_positions (List[Tuple[str, str]]): A list of tuples representing the current
                    occupied positions.

            Returns:
                bool: True if the drone can use the connection, False otherwise.
        """
        occupant_count = 0
        connection: Connection | None = None

        for source_pos, dest_pos in occupied_positions:
            if source_pos == source.name and dest_pos == dest.name:
                occupant_count += 1

        for con in cls.connections:
            if ((con.start == source.name and con.end == dest.name) or
                    (con.start == dest.name and con.end == source.name)):
                connection = con
                break

        if connection:
            return connection.metadata.max_link_capacity > occupant_count

        return False

    @staticmethod
    def _reset_visited_flags(Hubs: List[Hub]) -> None:
        """
            Reset the visited flags for all hubs in the provided list.

            Args:
                Hubs (List[Hub]): A list of Hub instances to reset the visited flags for.
        """

        for hub in Hubs:
            hub.visited = False

    @classmethod
    def _find_route_for_drone(cls, graph: Dict[str, List[Hub]]) -> List[Step]:
        """
            Find the optimal route for a drone using a modified Dijkstra's algorithm.

            Args:
                graph (Dict[str, List[Hub]]): An adjacency list representation of the graph.

            Returns:
                List[Step]: The optimal route for the drone.
        """

        route_queue: List[Tuple[float, Step, List[Step]]] = []
        best_route: List[Step] = []

        for hub_name in graph.keys():
            hub = cls._find_hub(hub_name)
            if hub and hub.type == HubType.start_hub:
                step = Step(0)
                step.dest = hub
                step.origin = hub
                heappush(route_queue, (0, step, [step]))
                hub.visited = True
                break

        while True:
            while True:
                try:
                    cost, current_step, current_route = heappop(route_queue)
                except IndexError:
                    raise InvalidMap("Invalid map no path found from start to\
                                     end.\n\n\tCheck that the connections \
                                     link them together.\
                                     and no blocked hub between them")

                current_dest: Hub = current_step.dest
                if current_dest.type == HubType.end_hub:
                    best_route = current_route
                    current_route = []
                    break
                # if there is no neighbors for the hub,
                # mean uncomplated route so remove them
                elif len(graph[current_dest.name]) == 0:
                    continue
                else:
                    break

            if not current_route:
                break

            next_turn = current_step.turn + 1
            for neighbor in graph[current_dest.name]:
                if not neighbor.visited:
                    neighbor.visited = True
                    turn_changes = cls._get_turn_changes(next_turn)
                    next_turn_changes = cls._get_turn_changes(next_turn + 1)

                    # print(turn_changes)
                    # print(next_turn_changes)

                    if neighbor.metadata.zone == ZoneTypes.restricted:
                        if (cls.can_use_connection(current_dest,
                                                   neighbor, turn_changes) and
                            cls.can_enter_hub(current_dest,
                                              neighbor,
                                              next_turn_changes)):
                            step = Step(next_turn + 1)
                            step.dest = neighbor
                            step.origin = current_dest
                            heappush(route_queue,
                                     (cost + 2, step, current_route + [step]))
                        else:
                            step = Step(next_turn)
                            step.dest = current_dest
                            step.origin = current_dest
                            heappush(route_queue,
                                     (cost + 1, step, current_route + [step]))
                            neighbor.visited = False

                    else:
                        if (cls.can_enter_hub(current_dest,
                                              neighbor,
                                              turn_changes)):
                            step = Step(next_turn)
                            step.dest = neighbor
                            step.origin = current_dest
                            heappush(route_queue,
                                     (cost + 1, step, current_route + [step]))
                        else:
                            step = Step(next_turn)
                            step.dest = current_dest
                            step.origin = current_dest
                            heappush(route_queue,
                                     (cost + 1, step, current_route + [step]))
                            neighbor.visited = False
        return best_route

    @classmethod
    def plan_all_drones(cls, drones: Dict[str, Drone],
                        connections: List[Connection],
                        hubs: Dict[str, Hub]
                        ) -> List[List[str]]:
        """
            Plan the routes for all drones based on the provided connections and hubs.

            Args:
                drones (Dict[str, Drone]): A dictionary of drones with drone IDs as keys.
                connections (List[Connection]): A list of connections between hubs.
                hubs (Dict[str, Hub]): A dictionary of hubs with hub names as keys.

            Returns:
                List[List[str]]: A list of lists, where each inner list represents the moves for a single turn.
        """

        cls.connections = connections
        cls.hubs = list(hubs.values())

        graph = GraphBuilder.build_adjacency_list(hubs, connections)

        for d_id in drones.keys():
            cls._reset_visited_flags(cls.hubs)
            cls.planned_routes[d_id] = PathFinding._find_route_for_drone(graph)
            cls._update_turns_changes(cls.planned_routes[d_id])

        turn_number: int = 1
        moves_per_turn: List[List[str]] = []

        while True:
            if all([step.turn < turn_number
                    for route in cls.planned_routes.values()
                    for step in route]):
                break
            turn_moves: List[str] = []
            for d_id in cls.planned_routes.keys():
                for step in cls.planned_routes[d_id]:
                    if (step.turn - 1 == turn_number and
                            step.dest.metadata.zone == ZoneTypes.restricted and
                            step.origin != step.dest):
                        label = f"{step.origin.name}-{step.dest.name}"
                        turn_moves.append(f"{d_id}-{label}")
                    elif step.turn == turn_number:
                        if step.dest != step.origin:
                            turn_moves.append(f"{d_id}-{step.dest.name}")
                    elif step.turn > turn_number:
                        break

            moves_per_turn.append(turn_moves)
            turn_number += 1

        return moves_per_turn
