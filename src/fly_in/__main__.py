import pyray as pr

from fly_in.controllers.controller import WorldController
from fly_in.factories.world_factory import build_world
from fly_in.parsing.parsing import ConfigParser, ParsingError
from fly_in.services.dijkstra import ReservedDijkstra
from fly_in.view.world import WorldView


def main() -> None:
    try:
        parser = ConfigParser("maps/challenger/01_the_impossible_dream.txt")
        config = parser.parse()

        pr.set_config_flags(pr.ConfigFlags.FLAG_MSAA_4X_HINT)
        pr.init_window(1080, 720, "Fly-in")
        pr.set_target_fps(60)

        model = build_world(config, ReservedDijkstra)

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
