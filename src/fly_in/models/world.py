from collections import deque
from pathlib import Path

import pyray as pr


from fly_in.models.drone import DroneModel
from fly_in.view.camera import Camera
from fly_in.models.hub import HubModel
from fly_in.models.connection import ConnectionModel


class WorldError(Exception):
    pass


class WorldModel:
    def __init__(self) -> None:
        self.drones: list[DroneModel] = []
        self.hubs: dict[str, HubModel] = {}
        self.connections: list[ConnectionModel] =  []

    def _copy_vector(self, vector: pr.Vector3) -> pr.Vector3:
        return pr.Vector3(
            vector.x, vector.y, vector.z
        )

    # TODO: prendre en parametre la liste des path
    def add_drone(
        self,
        start_point: pr.Vector3 = pr.Vector3(0.0, 0.0, 0.0),
    ):
        self.drones.append(DroneModel(
            start_point=start_point,
            hubs_path=deque([pr.Vector3(0.0, 0, 20.0), pr.Vector3(20.0, 0.0, 20.0)])
       ))

    def add_hub(
        self,
        name: str,
        color: pr.Color,
        start_point: pr.Vector3 = pr.Vector3(0.0, 0.0, 0.0),
    ):
        self.hubs[name] = HubModel(
            position=start_point,
            name=name,
            color=color
        )

    def add_connection(self, start_name: str, end_name: str) -> None:
        try:
            self.connections.append(ConnectionModel(
                self._copy_vector(self.hubs[start_name].position),
                self._copy_vector(self.hubs[end_name].position)
            ))
        except KeyError as e:
            raise WorldError(f"invalid hub name {e}")

    def update_state(self) -> None:
        for drone in self.drones:
            drone.animation = True
            drone.update_state()

