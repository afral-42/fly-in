import pyray as pr
import os
import math
from collections import deque
from fly_in.models.drone import DroneModel


class DroneView:
    def __init__(
        self,
        model: pr.Model,
    ) -> None:
        self.model = model

    def render(self, drone: DroneModel) -> None:
        rotation_axis = pr.Vector3(0, 1, 0)

        game_time = pr.get_time()
        animation_offset = math.sin(game_time * 3.0) * 0.5
        self.animated_position = pr.Vector3(
            drone.position.x,
            drone.position.y + animation_offset,
            drone.position.z
        )

        pr.draw_model_ex(
            self.model,
            self.animated_position,
            rotation_axis,
            drone.angle,
            drone.size,
            pr.WHITE
        )
