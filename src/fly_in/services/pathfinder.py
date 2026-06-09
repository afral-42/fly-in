from abc import ABC, abstractmethod


class Position:
    """Represents a point in the pathfinding graph.

    Attributes:
        x, y: Coordinates of the position in the map plane.
        hub_name: Identifier for the hub or synthetic flight node.
        is_restricted: Whether this position represents a restricted zone.
        is_flight_node: Whether this is a synthetic flight node.
        physical_connection: Optional tuple pointing to the real
            connection represented by a flight node.
        is_priority: Whether this position has routing priority.
        is_blocked: Whether this position is blocked and should be
            ignored when building graphs and routing.
    """
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
        """Compare positions by their `hub_name` for equality."""
        if not isinstance(other, Position):
            return False
        return self.hub_name == other.hub_name

    def __lt__(self, other: Position) -> bool:
        """Order positions for deterministic heaps, prioritizing
        `is_priority` positions.
        """
        if self.is_priority and not other.is_priority:
            return True
        elif not self.is_priority and other.is_priority:
            return False
        return self.hub_name < other.hub_name


class PathFinder(ABC):
    """Abstract base class for pathfinder implementations.

    Subclasses should implement an algorithm that can compute a time
    expanded path given hub and connection capacity constraints.
    """
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
        """Record reservations for a chosen path so subsequent
        route computations respect capacity constraints."""
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset any internal search state to allow another `solve()`
        invocation."""
        pass

    @abstractmethod
    def solve(self) -> list[Position] | None:
        """Compute and return a path from start to end or None.

        Returns a list of `Position` nodes representing the found
        route, or `None` if no route is available.
        """
        pass
