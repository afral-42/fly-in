import sys

import pyray as pr

from fly_in.controllers.controller import WorldController
from fly_in.factories.world_factory import build_world
from fly_in.parsing.arguments import get_map_path
from fly_in.parsing.parsing import ConfigParser
from fly_in.services.dijkstra import ReservedDijkstra
from fly_in.view.world import WorldView


def main() -> None:
    """Entry point for the Fly-in application.

    Parses the default configuration file, initializes rendering, and
    starts the world controller loop. Handles parsing and runtime
    exceptions gracefully and ensures the window is closed.
    """
    map_path = get_map_path()

    try:
        parser = ConfigParser(map_path)
        config = parser.parse()

        flags = (pr.ConfigFlags.FLAG_MSAA_4X_HINT)
        monitor = pr.get_current_monitor()
        screen_width = pr.get_monitor_width(monitor)
        screen_height = pr.get_monitor_height(monitor)

        pr.set_config_flags(flags)
        pr.set_trace_log_level(pr.TraceLogLevel.LOG_NONE)
        pr.init_window(screen_width, screen_height, "Fly-in - @abounoua")
        pr.set_target_fps(60)
        pr.toggle_fullscreen()

        model = build_world(config, ReservedDijkstra)

        with WorldView() as view:
            view.center_camera(model)
            controller = WorldController(view, model)
            controller.loop()

    except Exception as e:
        print(e)
        sys.exit(1)
    except KeyboardInterrupt:
        pass
    finally:
        pr.close_window()


if __name__ == "__main__":
    main()
