import heapq

from fly_in.services.pathfinder import PathFinder, Position


class ReservedDijkstra(PathFinder):
    """A Dijkstra-like pathfinder that reserves hub and connection slots.

    This implementation extends `PathFinder` to compute time-expanded
    paths while tracking reservations per-turn for hubs and
    connections to enforce capacity constraints.
    """

    def __init__(
        self,
        graph: dict[Position, list[Position]],
        start: Position,
        end: Position,
        hub_restrictions: dict[Position, int],
        connection_restrictions: dict[tuple[str, str], int],
    ) -> None:
        self.connection_reservation: dict[
            tuple[tuple[str, str], int], int
        ] = {}
        self.hub_reservation: dict[tuple[Position, int], int] = {}
        self.costs: list[tuple[int, Position]] = []
        self.graph = graph
        self.hub_restrictions = hub_restrictions
        self.connection_restrictions = {
            self.normalize_connection(connection): limit
            for connection, limit in connection_restrictions.items()
        }
        self.path: dict[Position, Position] = {}
        self.came_from: dict[tuple[Position, int], Position] = {}
        self.start = start
        self.end = end

    @staticmethod
    def normalize_connection(connection: tuple[str, str]) -> tuple[str, str]:
        """Normalize a connection tuple to a canonical ordering.

        Args:
            connection: A `(start, end)` tuple.

        Returns:
            A tuple with the items ordered `(min, max)` to treat
            connections as undirected for reservation lookups.
        """
        return min(connection), max(connection)

    def is_full(self, position: Position, turn: int) -> bool:
        """Return True if the given hub `position` is full at `turn`.

        Checks existing hub reservations against the configured hub
        restrictions.
        """
        reserved = self.hub_reservation.get((position, turn))
        restriction = self.hub_restrictions.get(position)

        if reserved is None or restriction is None:
            return False

        return reserved >= restriction

    def is_full_connection(
        self, position: Position, next: Position, turn: int
    ) -> bool:
        """Return True if the connection between `position` and `next`
        is full at the given `turn`.

        The method resolves whether a flight node or a physical
        connection should be used and checks reservations vs the
        configured connection capacities.
        """
        if position.is_flight_node and position.physical_connection:
            connection = self.normalize_connection(
                position.physical_connection
            )
        elif next.is_flight_node and next.physical_connection:
            connection = self.normalize_connection(next.physical_connection)
        else:
            connection = self.normalize_connection(
                (position.hub_name, next.hub_name)
            )

        reserved = self.connection_reservation.get((connection, turn))
        restriction = self.connection_restrictions.get(connection)

        if reserved is None or restriction is None:
            return False

        return reserved >= restriction

    def push_neighbors(self, position: Position, cost: int) -> None:
        """Push valid neighboring positions into the priority queue.

        Explores neighbor nodes for the next time step and records
        predecessor information used later to reconstruct the path.
        """
        next_turn = cost + 1

        for next in self.graph[position]:
            if (
                not self.is_full(next, next_turn)
                and not self.is_full_connection(position, next, cost)
                and (next, next_turn) not in self.came_from
            ):
                heapq.heappush(self.costs, (next_turn, next))
                self.came_from[(next, next_turn)] = position

        if (
            not position.is_flight_node
            and not self.is_full(position, next_turn)
            and (position, next_turn) not in self.came_from
        ):
            heapq.heappush(self.costs, (next_turn, position))
            self.came_from[(position, next_turn)] = position

    def solve(self) -> list[Position] | None:
        """Run the pathfinding algorithm and return a route.

        Returns a list of `Position` objects representing the path
        from `start` to `end`, or `None` if no path is found within a
        reasonable search limit.
        """
        heapq.heappush(self.costs, (0, self.start))

        while len(self.costs):
            cost, pos = heapq.heappop(self.costs)
            if pos == self.end:
                return self.compute_path(cost)

            if cost > 1000:
                return None

            self.push_neighbors(pos, cost)

        return None

    def add_reservations(self, path: list[Position]) -> None:
        """Add reservations for hubs and connections along `path`.

        Updates internal reservation maps to mark capacity usage per
        time-step for both hubs and traversed connections.
        """
        path.insert(0, self.start)
        for i, pos in enumerate(path, 0):
            if (pos, i) not in self.hub_reservation:
                self.hub_reservation[(pos, i)] = 0
            self.hub_reservation[(pos, i)] += 1

            if i < len(path) - 1:
                next_pos = path[i + 1]

                if pos == next_pos:
                    continue

                if pos.is_flight_node and pos.physical_connection:
                    connection = self.normalize_connection(
                        pos.physical_connection
                    )
                elif next_pos.is_flight_node and next_pos.physical_connection:
                    connection = self.normalize_connection(
                        next_pos.physical_connection
                    )
                else:
                    connection = self.normalize_connection(
                        (pos.hub_name, next_pos.hub_name)
                    )

                if (connection, i) not in self.connection_reservation:
                    self.connection_reservation[connection, i] = 0

                self.connection_reservation[(connection, i)] += 1

        path.pop(0)

    def reset(self) -> None:
        """Reset internal search state so the solver can be reused."""
        self.costs = []
        self.came_from = {}

    def compute_path(self, cost: int) -> list[Position]:
        """Reconstruct the path from internal predecessor maps.

        Args:
            cost: The total cost (time steps) to reach the goal.

        Returns:
            The list of `Position` nodes representing the path.
        """
        path: list[Position] = []
        pos = self.end

        while cost:
            path.append(pos)
            pos = self.came_from[pos, cost]
            cost -= 1

        path.reverse()
        self.add_reservations(path)
        return path
