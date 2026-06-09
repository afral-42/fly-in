import pyray as pr


class HubModel:
    def __init__(
        self,
        position: pr.Vector3,
        color: pr.Color,
        name: str,
        max_drones: int | None = None,
        radius: float = 4,
        height: float = 2,
        slices: int = 8,
    ) -> None:
        """Representation of a hub used for rendering.

        Args:
            position: 3D position of the hub.
            color: Display color for the hub.
            name: Hub identifier.
            max_drones: Optional capacity for the hub.
            radius: Visual radius for the hub cylinder.
            height: Visual height for the hub cylinder.
            slices: Number of radial slices for rendering.
        """
        self.position = position
        self.radius = radius
        self.color = color
        self.height = height
        self.slices = slices
