
from fly_in.parsing.schemas import FlyinConfig
from fly_in.services.dijkstra import Position


def build_restrictions(
    graph: dict[Position, list[Position]],
    config: FlyinConfig
) -> dict[Position, int]:
    restrictions: dict[Position, int] = {}
    for hub in config.hubs:
        restrictions[Position(hub.x, hub.y, hub.name)] = (
            hub.metadatas.max_drones
        )

    return restrictions


def build_connections(config: FlyinConfig) -> dict[tuple[str, str], int]:
    restrictions: dict[tuple[str, str], int] = {}
    for connection in config.connections:
        restrictions[(connection.start_name, connection.end_name)] = (
            connection.metadatas.max_link_capacity
        )

    return restrictions
