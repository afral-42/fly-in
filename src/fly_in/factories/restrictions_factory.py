from fly_in.parsing.schemas import FlyinConfig
from fly_in.services.pathfinder import Position


def build_restrictions(
    graph: dict[Position, list[Position]], config: FlyinConfig
) -> dict[Position, int]:
    """Build hub restrictions mapping from configuration.

    Creates a mapping from hub `Position` to the maximum number of
    drones allowed at that hub, based on the `FlyinConfig`.

    Args:
        graph: Graph of positions (unused but kept for API consistency).
        config: Parsed `FlyinConfig` with hub metadata.

    Returns:
        A dictionary mapping `Position` instances to their
        integer capacity limits.
    """
    restrictions: dict[Position, int] = {}
    for hub in config.hubs:
        restrictions[Position(hub.x, hub.y, hub.name)] = (
            hub.metadatas.max_drones
        )

    return restrictions


def build_connections(config: FlyinConfig) -> dict[tuple[str, str], int]:
    """Build connection capacity mapping from configuration.

    Args:
        config: Parsed `FlyinConfig` containing connection metadatas.

    Returns:
        A dictionary mapping `(start_name, end_name)` tuples to their
        integer max link capacity.
    """
    restrictions: dict[tuple[str, str], int] = {}
    for connection in config.connections:
        restrictions[(connection.start_name, connection.end_name)] = (
            connection.metadatas.max_link_capacity
        )

    return restrictions
