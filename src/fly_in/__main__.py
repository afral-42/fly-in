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

    SCALE = 10.0
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
            pr.Vector3(hub.x * SCALE, 0.0, hub.y * SCALE)
        )
    
    for connection in config.connections:
        model.add_connection(
            connection.start_name,
            connection.end_name
        )

    return model


def main() -> None:
    try:
        parser = ConfigParser("maps/hard/03_ultimate_challenge.txt")
        config = parser.parse()

        print(config.model_dump_json(indent=4))
    except ParsingError as e:
        print(e)

    try:
        pr.init_window(1920, 1080, "Fly-in")
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
