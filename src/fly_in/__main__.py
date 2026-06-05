from collections import deque
from typing import cast

import pyray as pr

from fly_in.controllers.controller import WorldController
from fly_in.models.world import WorldModel
from fly_in.parsing import ConfigParser, ParsingError
from fly_in.schemas import FlyinConfig, ZoneType
from fly_in.services.dijkstra import Position, ReservedDijkstra
from fly_in.view.world import WorldView


def build_graph(config: FlyinConfig) -> dict[Position, list[Position]]:
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


def build_restrictions(graph: dict, config: FlyinConfig) -> dict:
    restrictions = {}
    for hub in config.hubs:
        restrictions[Position(hub.x, hub.y, hub.name)] = (
            hub.metadatas.max_drones
        )

    return restrictions


def build_connections(config: FlyinConfig) -> dict:
    restrictions = {}
    for connection in config.connections:
        restrictions[(connection.start_name, connection.end_name)] = (
            connection.metadatas.max_link_capacity
        )

    return restrictions


def get_pr_color(color: str) -> pr.Color:
    return cast(pr.Color, getattr(pr, color.upper()))


def build_world(config: FlyinConfig) -> WorldModel:
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

    dijkstra = ReservedDijkstra(
        build_graph(config),
        Position(
            config.start_hub.x, config.start_hub.y, config.start_hub.name
        ),
        Position(config.end_hub.x, config.end_hub.y, config.end_hub.name),
        build_restrictions(build_graph(config), config),
        build_connections(config),
    )

    for i in range(config.nb_drones):
        path = []
        solved = dijkstra.solve()

        if solved is None:
            raise Exception("Path not found")
        for position in solved:
            path.append(pr.Vector3(position.x * SCALE, 0, position.y * SCALE))

        model.add_drone(
            deque(path),
            pr.Vector3(
                config.start_hub.x * SCALE, 3, config.start_hub.y * SCALE
            ),
        )
        dijkstra.reset()

    return model


def main() -> None:
    try:
        parser = ConfigParser("maps/easy/02_simple_fork.txt")
        config = parser.parse()

        print(config.model_dump_json(indent=4))

        pr.set_config_flags(pr.ConfigFlags.FLAG_MSAA_4X_HINT)
        pr.init_window(2080, 1280, "Fly-in")
        pr.set_target_fps(60)

        # model = WorldModel()
        # build_world(config)
        # model.add_hub("start", pr.RED, pr.Vector3(0.0, 0.0, 0.0))
        # model.add_hub("1", pr.BLUE, pr.Vector3(0.0, 0.0, 20.0))
        # model.add_hub("end", pr.GOLD, pr.Vector3(20.0, 0.0, 20.0))
        # model.add_drone(pr.Vector3(0.0, 2.0, 0.0))
        # model.add_connection("start", "end")

        model = build_world(config)

        with WorldView() as view:
            view.center_camera(model)
            controller = WorldController(view, model)
            controller.loop()

    except ParsingError as e:
        print(e)
    except Exception as e:
        print(e)
    except KeyboardInterrupt:
        pass
    finally:
        pr.close_window()


if __name__ == "__main__":
    main()
