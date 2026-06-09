import math
import random

import pyray as pr

from fly_in.models.drone import DroneModel


class DroneView:
    def __init__(
        self,
        model: pr.Model,
    ) -> None:
        """View responsible for rendering drone models with simple
        animation offsets.

        Args:
            model: Loaded `pyray.Model` used to draw each drone.
        """
        self.model = model
        self.animation_map: dict[DroneModel, dict[str, float]] = {}

    def render(self, drone: DroneModel) -> None:
        """Render a single `DroneModel` with a bobbing animation.

        Args:
            drone: The `DroneModel` instance to render.
        """
        if drone not in self.animation_map:
            self.animation_map[drone] = {
                "animation_phase_offset": random.uniform(0.0, math.pi * 2),
                "animation_speed": random.uniform(2.0, 4.0),
                "animation_amplitude": random.uniform(0.3, 1.0),
            }

        rotation_axis = pr.Vector3(0, 1, 0)

        game_time = pr.get_time()

        animation_offset = (
            math.sin(
                (game_time * self.animation_map[drone]["animation_speed"])
                + self.animation_map[drone]["animation_phase_offset"]
            )
            * self.animation_map[drone]["animation_amplitude"]
        )

        self.animated_position = pr.Vector3(
            drone.position.x,
            drone.position.y + animation_offset,
            drone.position.z,
        )

        pr.draw_model_ex(
            self.model,
            self.animated_position,
            rotation_axis,
            drone.angle,
            drone.size,
            pr.WHITE,
        )
