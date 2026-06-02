from collections import deque
import random

from fly_in.controllers.controller import WorldController
from fly_in.models.world import WorldModel
from fly_in.parsing import ConfigParser, ParsingError
import pyray as pr

from fly_in.schemas import FlyinConfig
from fly_in.services.dijkstra import Position, ReservedDijkstra
from fly_in.view.world import WorldView


def build_graph(config: FlyinConfig) -> dict:
    # 1. On crée un dictionnaire rapide pour retrouver les Positions grâce au nom du hub
    # (On inclut bien tous les hubs, y compris start et end pour être sûr)
    all_hubs = config.hubs + [config.start_hub, config.end_hub]
    positions_by_name = {
        hub.name: Position(hub.x, hub.y, hub.name) 
        for hub in all_hubs
    }

    # 2. On initialise le graphe avec des listes vides pour chaque Position
    graph = {pos: [] for pos in positions_by_name.values()}

    # 3. On lit les connexions et on branche les tuyaux !
    for connection in config.connections:
        if connection.start_name in positions_by_name and connection.end_name in positions_by_name:
            start_pos = positions_by_name[connection.start_name]
            end_pos = positions_by_name[connection.end_name]
            
            # On ajoute le voisin à la liste du hub de départ
            graph[start_pos].append(end_pos)
            graph[end_pos].append(start_pos)

    return graph

def build_restrictions(graph: dict, config: FlyinConfig) -> dict:
    restrictions = {}
    for hub in config.hubs:
        restrictions[Position(hub.x, hub.y, hub.name)] = hub.metadatas.max_drones
    
    return restrictions


def get_pr_color(color: str) -> pr.Color:
    return getattr(pr, color.upper())

def build_world(config: FlyinConfig) -> WorldModel:
    model = WorldModel()

    SCALE = 12.0
    model.add_hub(
        config.start_hub.name,
        get_pr_color(config.start_hub.metadatas.color),
        pr.Vector3(config.start_hub.x * SCALE, 0.0, config.start_hub.y * SCALE)
    )
    model.add_hub(
        config.end_hub.name,
        get_pr_color(config.end_hub.metadatas.color),
        pr.Vector3(config.end_hub.x * SCALE, 0.0, config.end_hub.y * SCALE)
    )

    for hub in config.hubs:
        model.add_hub(
            hub.name,
            get_pr_color(hub.metadatas.color),
            pr.Vector3(hub.x * SCALE, 0.0, hub.y * SCALE),
            hub.metadatas.max_drones
        )
        model.add_text(
            str(hub.metadatas.max_drones),
            pr.Vector3(hub.x * SCALE, 2.1, hub.y * SCALE),
            3.0,
            get_pr_color(hub.metadatas.color)
        )
    
    for connection in config.connections:
        model.add_connection(
            connection.start_name,
            connection.end_name
        )

    # Test de notre djikstra
    dijkstra = ReservedDijkstra(
        build_graph(config),
        Position(config.start_hub.x, config.start_hub.y, config.start_hub.name),
        Position(config.end_hub.x, config.end_hub.y, config.end_hub.name),
        build_restrictions(build_graph(config), config),
        {}
    )

    for i in range(config.nb_drones):
        path = []
        solved = dijkstra.solve()
        if solved is None:
            raise Exception
        for position in solved:
            path.append(pr.Vector3(position.x * SCALE, 0, position.y * SCALE))

        model.add_drone(
            deque(path),
            pr.Vector3(config.start_hub.x * SCALE, 3, config.start_hub.y * SCALE),
        )
        dijkstra.reset()

    return model


def main() -> None:
    try:
        parser = ConfigParser("maps/hard/01_maze_nightmare.txt")
        config = parser.parse()

        print(config.model_dump_json(indent=4))
    except ParsingError as e:
        print(e)

    try:
        pr.set_config_flags(pr.ConfigFlags.FLAG_MSAA_4X_HINT)
        pr.init_window(1080, 720, "Fly-in")
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

    except Exception as e:
        print(e)
    except KeyboardInterrupt:
        pass
    finally:
        pr.close_window()


if __name__ == "__main__":
    main()
