import heapq


class Position:
    def __init__(
        self,
        x: float,
        y: float,
        hub_name: str,
        is_restricted: bool = False,
        is_flight_node: bool = False,
        physical_connection: tuple[str, str] | None = None,
        is_priority: bool = False,
        is_blocked: bool = False,
    ) -> None:
        self.x = x
        self.y = y
        self.hub_name = hub_name
        self.is_restricted = is_restricted
        self.is_flight_node = is_flight_node
        self.physical_connection = physical_connection
        self.is_priority = is_priority
        self.is_blocked = is_blocked

    def __hash__(self) -> int:
        return hash(self.hub_name)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Position):
            return False
        return self.hub_name == other.hub_name

    def __lt__(self, other: Position) -> bool:
        if self.is_priority and not other.is_priority:
            return True
        elif not self.is_priority and other.is_priority:
            return False
        return self.hub_name < other.hub_name


class ReservedDijkstra:
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
        return min(connection), max(connection)

    def is_full(self, position: Position, turn: int) -> bool:
        reserved = self.hub_reservation.get((position, turn))
        restriction = self.hub_restrictions.get(position)

        if reserved is None or restriction is None:
            return False

        return reserved >= restriction

    def is_full_connection(
        self, position: Position, next: Position, turn: int
    ) -> bool:
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
        self.costs = []
        self.came_from = {}

    def compute_path(self, cost: int) -> list[Position]:
        path: list[Position] = []
        pos = self.end

        while cost:
            path.append(pos)
            pos = self.came_from[pos, cost]
            cost -= 1

        path.reverse()
        print([p.hub_name for p in path])
        self.add_reservations(path)
        return path
