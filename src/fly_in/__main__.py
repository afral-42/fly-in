from fly_in.parsing import ConfigParser, ParsingError
from fly_in.view.controller import GameController
import pyray as pr


def main() -> None:
    try:
        parser = ConfigParser("salut.txt")
        config = parser.parse()

        print(config.model_dump_json(indent=4))
    except ParsingError as e:
        print(e)

    with GameController() as controller:
        controller.add_drone(pr.Vector3(0.0, 2.0, 0.0))
        controller.add_hub(pr.Vector3(0.0, 0.0, 0.0))
        controller.loop()


if __name__ == "__main__":
    main()
