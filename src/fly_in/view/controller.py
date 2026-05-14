from types import TracebackType
from typing import Self

import pyray as pr
import os
import math

from fly_in.view.camera import Camera
from fly_in.view.drone import Drone
from fly_in.view.hub import Hub


class GameController:
    def __init__(self) -> None:
        self.drones: list[Drone] = []
        self.hubs: list[Hub] = []

        self.camera = Camera(
            up=pr.Vector3(0.0, 1.0, 0.0),
            fov=45.0,
            projection=pr.CameraProjection(
                pr.CameraProjection.CAMERA_PERSPECTIVE
            ),
            target=pr.Vector3(0.0, 0.0, 0.0),
            position=pr.Vector3(0.0, 10.0, 10.0)
        )

        folder = os.path.dirname(os.path.abspath(__file__))
        self.model_path = os.path.join(folder, "models", "dji_spark.glb")

    def __enter__(self) -> Self:
        pr.init_window(2080, 1440, "Fly-in")
        pr.set_target_fps(60)
        self.drone_model = pr.load_model(self.model_path)

        return self

    def __exit__(
        self, 
        exc_type: type[BaseException] | None, 
        exc_val: BaseException | None, 
        exc_tb: TracebackType | None
    ) -> None:
        pr.unload_model(self.drone_model)
        pr.close_window()

    def add_drone(self, start_point: pr.Vector3 = pr.Vector3(0.0, 0.0, 0.0)):
        self.drones.append(Drone(
            model=self.drone_model,
            start_point=start_point,
        ))

    def add_hub(self, start_point: pr.Vector3 = pr.Vector3(0.0, 0.0, 0.0)):
        self.hubs.append(Hub(
            position=start_point
        ))

    def loop(self):
        while not pr.window_should_close():
            pr.begin_drawing()
            pr.clear_background(pr.WHITE)
            self.camera.begin_3d()
            pr.draw_grid(20, 2.0)
            
            for drone in self.drones:
                drone.render()
            
            for hub in self.hubs:
                hub.render()
            
            self.camera.end_3d()
            pr.end_drawing()
