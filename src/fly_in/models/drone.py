import pyray as pr
import os
import math
from collections import deque
from enum import Enum, auto


class DroneState(Enum):
    PARKED = auto()
    TRANSIT = auto()


class DroneModel():
    def __init__(
        self,
        start_point: pr.Vector3,
        hubs_path: deque[pr.Vector3],
        speed: float = 0.2,
        size: pr.Vector3 = pr.Vector3(0.25, 0.25, 0.25)
    ) -> None:
        self.position = start_point
        self.hubs_path = hubs_path
        self.target = self.position
        self.animation = False
        self.speed = speed
        self.angle = 0
        self.size = size
        self.state = DroneState.PARKED
        self.parked_target = self.target
        self.parked_zone = self.position

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

        if direction_norm == 0:
            return pr.Vector3(0.0, 0.0, 0.0)

        normalized_direction = pr.Vector3(
            direction.x / direction_norm,
            direction.y / direction_norm,
            direction.z / direction_norm
        )
    
        return normalized_direction
    
    def prepare_takeoff(self) -> None:
        if self.state == DroneState.PARKED and len(self.hubs_path) > 0:
            self.target = self.hubs_path.popleft()
            self.animation = True

    def update_state(self) -> None:
        if not self.animation:
            self.position = pr.Vector3(
                self.parked_target.x, 
                self.position.y, 
                self.parked_target.z
            )

        else:
            self._align_direction(self.parked_target)
            direction = self._get_normalized_direction(self.parked_target, self.position)
            
            dx = self.position.x - self.parked_target.x
            dz = self.position.z - self.parked_target.z
            distance_2d = math.sqrt(dx**2 + dz**2)

            if distance_2d < self.speed:
                self.state = DroneState.PARKED
                self.animation = False
                self.parked_zone = self.target
            else:
                self.state = DroneState.TRANSIT
                self.position = pr.Vector3(
                    self.position.x + direction.x * self.speed,
                    self.position.y,
                    self.position.z + direction.z * self.speed
                )
