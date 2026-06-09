
from collections import deque
from typing import cast
import pyray as pr
from fly_in.factories.graph_factory import build_graph
from fly_in.factories.restrictions_factory import (
    build_connections, build_restrictions
)
from fly_in.models.world import WorldModel
from fly_in.parsing.schemas import FlyinConfig
from fly_in.services.pathfinder import PathFinder, Position


def get_pr_color(color: str) -> pr.Color:
    """Convert a color name to a pyray `Color` object.

    Args:
        color: Name of the color (case-insensitive) corresponding to
            an attribute on the `pyray` module (e.g., "white").

    Returns:
        The `pyray.Color` value for the requested color.
    """

    return cast(pr.Color, getattr(pr, color.upper()))


def build_world(config: FlyinConfig, solver: type[PathFinder]) -> WorldModel:
    """Construct a `WorldModel` from a `FlyinConfig` and pathfinder.

    This builds hubs, connections, text annotations and drone paths
    according to the provided configuration. It uses the provided
    `solver` class (a subclass of `PathFinder`) to compute routes for
    each drone and applies capacity/restriction rules when building
    the world model.

    Args:
        config: The validated `FlyinConfig` describing the map.
        solver: A `PathFinder` subclass used to compute drone paths.

    Returns:
        A populated `WorldModel` ready for rendering and simulation.
    """

    model = WorldModel()

    SCALE = 12.0
    model.add_hub(
        config.start_hub.name,
        get_pr_color(config.start_hub.metadatas.color),
        pr.Vector3(
            config.start_hub.x * SCALE, 0.0, config.start_hub.y * SCALE
        ),
    )
    model.add_hub(
        config.end_hub.name,
        get_pr_color(config.end_hub.metadatas.color),
        pr.Vector3(config.end_hub.x * SCALE, 0.0, config.end_hub.y * SCALE),
    )

    for hub in config.hubs:
        model.add_hub(
            hub.name,
            get_pr_color(hub.metadatas.color),
            pr.Vector3(hub.x * SCALE, 0.0, hub.y * SCALE),
            hub.metadatas.max_drones,
        )
        model.add_text(
            str(hub.metadatas.max_drones),
            pr.Vector3(hub.x * SCALE, 2.1, hub.y * SCALE),
            3.0,
            get_pr_color(hub.metadatas.color),
        )

    all_hubs = config.hubs + [config.start_hub, config.end_hub]
    hubs_by_name = {hub.name: hub for hub in all_hubs}
    for connection in config.connections:
        model.add_connection(connection.start_name, connection.end_name)
        start_hub = hubs_by_name[connection.start_name]
        end_hub = hubs_by_name[connection.end_name]

        model.add_text(
            str(connection.metadatas.max_link_capacity),
            pr.Vector3(
                ((start_hub.x + end_hub.x) / 2) * SCALE,
                1.5,
                ((start_hub.y + end_hub.y) / 2) * SCALE,
            ),
            3.0,
            pr.LIGHTGRAY,
            pr.BLACK,
        )

    algo = solver(
        build_graph(config),
        Position(
            config.start_hub.x, config.start_hub.y, config.start_hub.name
        ),
        Position(config.end_hub.x, config.end_hub.y, config.end_hub.name),
        build_restrictions(build_graph(config), config),
        build_connections(config),
    )

    count = 0
    for i in range(config.nb_drones):
        path = []
        solved = algo.solve()

        if solved is None:
            raise Exception("Path not found, please retry with a valid map")
        for position in solved:
            path.append(pr.Vector3(position.x * SCALE, 0, position.y * SCALE))

        if len(path) > count:
            count = len(path)

        model.add_drone(
            deque(path),
            pr.Vector3(
                config.start_hub.x * SCALE, 3, config.start_hub.y * SCALE
            ),
        )
        algo.reset()

    model.add_hud_text(
        f"Total cost: {count}", 10, 30, 30, pr.BLACK
    )

    return model
