from collections import defaultdict, deque
import math

import pyray as pr


from fly_in.models.drone import DroneModel, DroneState
from fly_in.models.hud_text import HudTextModel
from fly_in.models.text import TextModel
from fly_in.models.hub import HubModel
from fly_in.models.connection import ConnectionModel


class WorldError(Exception):
    """General exception for world model related errors."""


class WorldModel:
    """In-memory representation of the simulation world.

    Holds hubs, connections, drones, and text elements used by the
    renderer and the controller to run the simulation.
    """

    def __init__(self) -> None:
        self.drones: list[DroneModel] = []
        self.hubs: dict[str, HubModel] = {}
        self.connections: list[ConnectionModel] = []
        self.texts: list[TextModel] = []
        self.hud_texts: list[HudTextModel] = []
        self.count = 0

    def _copy_vector(self, vector: pr.Vector3) -> pr.Vector3:
        """Return a shallow copy of a `pyray.Vector3`.

        This helper avoids sharing mutable `Vector3` instances between
        model components.
        """
        return pr.Vector3(vector.x, vector.y, vector.z)

    def add_drone(
        self,
        hubs_path: deque[pr.Vector3],
        start_point: pr.Vector3 = pr.Vector3(0.0, 0.0, 0.0),
    ) -> None:
        """Append a new `DroneModel` to the world.

        Args:
            hubs_path: A deque of `Vector3` positions representing the
                planned path for the drone.
            start_point: Initial position for the drone.
        """
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
        """Add or replace a hub in the world.

        Args:
            name: Hub identifier.
            color: Display color.
            start_point: Hub position as `Vector3`.
            max_drones: Optional capacity of the hub.
        """
        self.hubs[name] = HubModel(
            position=start_point, name=name, color=color, max_drones=max_drones
        )

    def add_connection(self, start_name: str, end_name: str) -> None:
        """Create a visual connection between two named hubs.

        Raises `WorldError` if either hub name is unknown.
        """
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
        """Add a 3D text element to the world.

        Args:
            text: The string to render.
            position: 3D position where the text should appear.
            size: Visual size of the text plane.
            background_color: Optional background color to clear.
            color: Text color.
        """
        self.texts.append(
            TextModel(text, position, background_color, size, color)
        )

    def add_hud_text(
        self,
        text: str,
        position_x: int,
        position_y: int,
        size: int = 0,
        color: pr.Color = pr.BLACK,
    ) -> None:
        """Add a HUD text entry displayed in 2D overlay coordinates.

        Args:
            text: The string to render.
            position_x: X pixel coordinate.
            position_y: Y pixel coordinate.
            size: Font size for the HUD text.
            color: Text color.
        """
        self.hud_texts.append(
            HudTextModel(text, position_x, position_y, size, color)
        )

    def start_animation(self) -> None:
        """Trigger takeoff preparation for all parked drones."""
        if not all(
            [drone.state == DroneState.PARKED for drone in self.drones]
        ):
            return

        for drone in self.drones:
            drone.prepare_takeoff()

    def increase_speed(self) -> None:
        """Increase the simulation speed multiplier for all drones."""
        for drone in self.drones:
            drone.speed *= 1.2

    def decrease_speed(self) -> None:
        """Decrease the simulation speed multiplier for all drones."""
        for drone in self.drones:
            drone.speed *= 0.8

    def discard_drones(
        self, positions: dict[tuple[float, float], list[DroneModel]]
    ) -> None:
        """Spread parked drones around a hub position to avoid overlap.

        Args:
            positions: Mapping from 2D hub positions (x,z) to lists of
                `DroneModel` parked at that location.
        """
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
        """Compute parked target positions for drones to avoid collisions.

        Aggregates drones by their intended target position and calls
        `discard_drones` to distribute them visually.
        """
        positions = defaultdict(list)

        for drone in self.drones:
            pos_key = (drone.target.x, drone.target.z)
            positions[pos_key].append(drone)

        self.discard_drones(positions)

    def update_state(self) -> None:
        """Advance the world state by updating all drones.

        Recomputes parked targets and updates each drone's internal
        state for the simulation step.
        """
        self.get_target_parked_point()
        for drone in self.drones:
            drone.update_state()
