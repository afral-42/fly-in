from collections import deque
import random

from fly_in.controllers.controller import WorldController
from fly_in.models.world import WorldModel
from fly_in.parsing import ConfigParser, ParsingError
import pyray as pr

from fly_in.schemas import FlyinConfig
from fly_in.view.world import WorldView



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


    for i in range(config.nb_drones):
        # 1. On choisit une taille de parcours aléatoire (au moins 1 hub, au maximum tous)
        # Tu peux changer le '1' si tu veux qu'ils fassent des trajets plus longs minimum
        nb_hubs_to_visit = random.randint(1, len(config.hubs))

        # 2. On tire au sort des INDEX, et on les TRIE pour respecter l'ordre original
        random_indices = sorted(random.sample(range(len(config.hubs)), nb_hubs_to_visit))

        # 3. On construit la 'deque' uniquement avec les hubs correspondants à ces index
        random_path = deque([
            pr.Vector3(config.hubs[idx].x * SCALE, 0, config.hubs[idx].y * SCALE) 
            for idx in random_indices
        ])

        # 4. On ajoute le drone avec son chemin personnalisé
        model.add_drone(
            random_path,
            pr.Vector3(config.start_hub.x * SCALE, 3, config.start_hub.y * SCALE),
        )

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
