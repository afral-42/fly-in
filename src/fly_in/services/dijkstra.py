import heapq


class Position:
    def __init__(self, x: int, y: int, hub_name: str) -> None:
        self.x = x
        self.y = y
        self.hub_name = hub_name

    def __hash__(self) -> int:
        return hash(self.hub_name)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Position):
            return False
        return self.hub_name == other.hub_name

    def __lt__(self, other: Position) -> bool:
        return self.hub_name < other.hub_name


class ReservedDijkstra:
    def __init__(
        self,
        graph: dict[Position, list[Position]],
        start: Position,
        end: Position,
        hub_restrictions: dict[Position, int],
        connection_restrictions: dict[tuple[str, str], int]
    ) -> None:
        self.connection_reservation: dict[tuple[tuple[str, str], int], int] = {}
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

    def is_full_connection(self, position: Position, next: Position, turn: int) -> bool:
        connection = self.normalize_connection((position.hub_name, next.hub_name))
        reserved = self.connection_reservation.get((connection, turn))
        restriction = self.connection_restrictions.get(connection)

        if reserved is None or restriction is None:
            return False

        return reserved >= restriction


    def push_neighbors(self, position: Position, cost: int) -> None:
        next_turn = cost + 1

        for next in self.graph[position]:
            if (
                not self.is_full(next, next_turn) and
                not self.is_full_connection(position, next, next_turn) and
                (next, next_turn) not in self.came_from
            ):
                heapq.heappush(self.costs, (next_turn, next))
                self.came_from[(next, next_turn)] = position

        if (
            not self.is_full(position, next_turn) and
            (position, next_turn) not in self.came_from
        ):
            heapq.heappush(self.costs, (next_turn, position))
            self.came_from[(position, next_turn)] = position

    def solve(self) -> list[Position] | None:
        heapq.heappush(self.costs, (0, self.start))

        while len(self.costs):
            cost, pos = heapq.heappop(self.costs)
            if pos == self.end:
                return self.compute_path(cost)

            self.push_neighbors(pos, cost)

    def add_reservations(self, path: list[Position]) -> None:
        for i in range(0, len(path) - 1):
            prev, next = path[i].hub_name, path[i + 1].hub_name
            connection = self.normalize_connection((prev, next))
            if (connection, i) not in self.connection_reservation:
                self.connection_reservation[(connection, i)] = 0
            self.connection_reservation[(connection, i)] += 1

        for i, pos in enumerate(path, 1):
            if (pos, i) not in self.hub_reservation:
                self.hub_reservation[(pos, i)] = 0
            self.hub_reservation[(pos, i)] += 1


    def reset(self) -> None:
        self.costs = []
        self.came_from = {}

    def compute_path(self, cost: int) -> list[Position]:
        path: list[Position] = []
        pos = self.end

        while (cost):
            path.append(pos)
            pos = self.came_from[pos, cost]
            cost -= 1

        path.reverse()
        self.add_reservations(path)
        return path
