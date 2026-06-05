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
        self.position = position
        self.radius = radius
        self.color = color
        self.height = height
        self.slices = slices
