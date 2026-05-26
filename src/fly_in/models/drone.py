import pyray as pr
import os
import math
from collections import deque


class DroneModel():
    def __init__(
        self,
        start_point: pr.Vector3,
        hubs_path: deque[pr.Vector3],
        speed: float = 0.1,
        size: pr.Vector3 = pr.Vector3(0.25, 0.25, 0.25)
    ) -> None:
        self.position = start_point
        self.hubs_path = hubs_path
        self.target = hubs_path.popleft()
        self.animation = False
        self.speed = speed
        self.angle = 0
        self.size = size

    def _align_direction(self, target: pr.Vector3) -> None:
        dx = target.x - self.position.x
        dz = target.z - self.position.z
        
        angle = math.degrees(math.atan2(dx, dz))
        self.angle = angle - 90

    def _get_normalized_direction(
        self,
        target: pr.Vector3,
        position: pr.Vector3
    ) -> pr.Vector3:
        direction = pr.Vector3(
            target.x - position.x,
            target.y - position.y,
            target.z - position.z
        )
        direction_norm = math.sqrt(
            direction.x**2 + direction.y**2 + direction.z**2
        )
        normalized_direction = pr.Vector3(
            direction.x / direction_norm,
            direction.y / direction_norm,
            direction.z / direction_norm
        )
    
        return normalized_direction
    

    def update_state(self) -> None:
        if self.animation:
            self._align_direction(self.target)
            direction = self._get_normalized_direction(self.target, self.position)

            if direction.x < 0.1 and direction.y < 0.1 and direction.z < 0.1:
                if len(self.hubs_path):
                    self.target = self.hubs_path.popleft()
            self.position = pr.Vector3(
                self.position.x + direction.x * self.speed,
                self.position.y,
                self.position.z + direction.z * self.speed
            )
