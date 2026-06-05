from collections import defaultdict, deque
import math

import pyray as pr


from fly_in.models.drone import DroneModel, DroneState
from fly_in.models.hud_text import HudText
from fly_in.models.text import TextModel
from fly_in.models.hub import HubModel
from fly_in.models.connection import ConnectionModel


class WorldError(Exception):
    pass


class WorldModel:
    def __init__(self) -> None:
        self.drones: list[DroneModel] = []
        self.hubs: dict[str, HubModel] = {}
        self.connections: list[ConnectionModel] = []
        self.texts: list[TextModel] = []
        self.hud_texts: list[HudText] = []
        self.count = 0

    def _copy_vector(self, vector: pr.Vector3) -> pr.Vector3:
        return pr.Vector3(vector.x, vector.y, vector.z)

    # TODO: prendre en parametre la liste des path
    def add_drone(
        self,
        hubs_path: deque[pr.Vector3],
        start_point: pr.Vector3 = pr.Vector3(0.0, 0.0, 0.0),
    ) -> None:
        self.drones.append(
            DroneModel(start_point=start_point, hubs_path=hubs_path)
        )

    def add_hub(
        self,
        name: str,
        color: pr.Color,
        start_point: pr.Vector3 = pr.Vector3(0.0, 0.0, 0.0),
        max_drones: int | None = None,
    ) -> None:
        self.hubs[name] = HubModel(
            position=start_point, name=name, color=color, max_drones=max_drones
        )

    def add_connection(self, start_name: str, end_name: str) -> None:
        try:
            self.connections.append(
                ConnectionModel(
                    self._copy_vector(self.hubs[start_name].position),
                    self._copy_vector(self.hubs[end_name].position),
                )
            )
        except KeyError as e:
            raise WorldError(f"invalid hub name {e}")

    def add_text(
        self,
        text: str,
        position: pr.Vector3,
        size: float,
        background_color: pr.Color | None = None,
        color: pr.Color = pr.BLACK,
    ) -> None:
        self.texts.append(
            TextModel(text, position, background_color, size, color)
        )


    def add_hud_text(
        self,
        text: str,
        position: pr.Vector3,
        size: float = 0.0,
        background_color: pr.Color | None = None,
        color: pr.Color = pr.BLACK,
    ) -> None:
        self.hud_texts.append(
            TextModel(text, position, background_color, size, color)
        )

    def start_animation(self) -> None:
        if not all(
            [drone.state == DroneState.PARKED for drone in self.drones]
        ):
            return

        for drone in self.drones:
            drone.prepare_takeoff()

    def increase_speed(self) -> None:
        for drone in self.drones:
            drone.speed *= 1.2

    def decrease_speed(self) -> None:
        for drone in self.drones:
            drone.speed *= 0.8

    def discard_drones(
        self, positions: dict[tuple[float, float], list[DroneModel]]
    ) -> None:
        spacing = 3.0

        for target_pos, drones in positions.items():
            nb_drones = len(drones)

            if nb_drones > 1:
                angle_step = (2 * math.pi) / nb_drones

                for i, drone in enumerate(drones):
                    target_x, target_z = target_pos
                    new_x = target_x + (math.cos(i * angle_step) * spacing)
                    new_z = target_z + (math.sin(i * angle_step) * spacing)

                    drone.parked_target = pr.Vector3(
                        new_x, drone.position.y, new_z
                    )

            else:
                target_x, target_z = target_pos
                drones[0].parked_target = pr.Vector3(
                    target_x, drones[0].position.y, target_z
                )

    def get_target_parked_point(self) -> None:
        positions = defaultdict(list)

        for drone in self.drones:
            pos_key = (drone.target.x, drone.target.z)
            positions[pos_key].append(drone)

        self.discard_drones(positions)

    def update_state(self) -> None:
        self.get_target_parked_point()
        for drone in self.drones:
            drone.update_state()
