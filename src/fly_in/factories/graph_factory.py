
from fly_in.parsing.schemas import FlyinConfig, ZoneType
from fly_in.services.pathfinder import Position


def build_graph(config: FlyinConfig) -> dict[Position, list[Position]]:
    """Build a graph of positions from a FlyinConfig.

    The graph maps `Position` nodes to the list of adjacent `Position`
    nodes. Restricted hubs are replaced by intermediate flight nodes
    to represent no-fly zones. Blocked hubs are omitted.

    Args:
        config: Parsed `FlyinConfig` containing hubs and connections.

    Returns:
        A dictionary mapping `Position` objects to lists of neighbor
        `Position` objects representing the connectivity of the map.
    """
    all_hubs = config.hubs + [config.start_hub, config.end_hub]
    positions_by_name = {
        hub.name: Position(
            hub.x,
            hub.y,
            hub.name,
            hub.metadatas.zone == ZoneType.RESTRICTED,
            is_priority=hub.metadatas.zone == ZoneType.PRIORITY,
            is_blocked=hub.metadatas.zone == ZoneType.BLOCKED,
        )
        for hub in all_hubs
    }

    graph: dict[Position, list[Position]] = {
        pos: [] for pos in positions_by_name.values()
    }

    for connection in config.connections:
        if (
            connection.start_name in positions_by_name
            and connection.end_name in positions_by_name
        ):
            start_pos = positions_by_name[connection.start_name]
            end_pos = positions_by_name[connection.end_name]

            if start_pos.is_blocked or end_pos.is_blocked:
                continue
            real_edge = (start_pos.hub_name, end_pos.hub_name)

            if end_pos.is_restricted:
                middle_point = Position(
                    (start_pos.x + end_pos.x) / 2,
                    (start_pos.y + end_pos.y) / 2,
                    f"{start_pos.hub_name}-{end_pos.hub_name}",
                    False,
                    True,
                    real_edge,
                )
                if middle_point not in graph:
                    graph[middle_point] = []
                graph[start_pos].append(middle_point)
                graph[middle_point].append(end_pos)
            else:
                graph[start_pos].append(end_pos)

            if start_pos.is_restricted:
                middle_point = Position(
                    (start_pos.x + end_pos.x) / 2,
                    (start_pos.y + end_pos.y) / 2,
                    f"{end_pos.hub_name}-{start_pos.hub_name}",
                    False,
                    True,
                    real_edge,
                )
                if middle_point not in graph:
                    graph[middle_point] = []
                graph[end_pos].append(middle_point)
                graph[middle_point].append(start_pos)
            else:
                graph[end_pos].append(start_pos)

    return graph
