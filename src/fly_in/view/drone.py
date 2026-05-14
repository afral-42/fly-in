import pyray as pr
import os
import math


class Drone():
    def __init__(
        self,
        model: pr.Model,
        start_point: pr.Vector3,
        size: float = 0.20
    ) -> None:
        self.model = model
        self.position = start_point
        self.size = size
    
    def render(self) -> None:
        game_time = pr.get_time()
        animation_offset = math.sin(game_time * 3.0) * 0.5
        self.animated_position = pr.Vector3(
            self.position.x,
            self.position.y + animation_offset,
            self.position.z
        )
        pr.draw_model(self.model, self.animated_position, self.size, pr.WHITE)
