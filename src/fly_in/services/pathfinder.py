from abc import ABC, abstractmethod



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


class PathFinder(ABC):
    @abstractmethod
    def __init__(
        self,
        graph: dict[Position, list[Position]],
        start: Position,
        end: Position,
        hub_restrictions: dict[Position, int],
        connection_restrictions: dict[tuple[str, str], int],
    ) -> None:
        pass

    @abstractmethod
    def add_reservations(self, path: list[Position]) -> None:
        pass

    @abstractmethod
    def reset(self) -> None:
        pass
    
    @abstractmethod
    def solve(self) -> list[Position] | None:
        pass
