import pyray as pr


class Hub:
    def __init__(
        self,
        position: pr.Vector3
    ) -> None:
        self.position = position
        self.radius = 2.0

    def render(self) -> None:
        color = pr.RED

        pr.draw_cylinder(
            self.position,
            self.radius,
            self.radius,
            2,
            8,
            color
        )
        pr.draw_cylinder_wires(
            self.position,
            self.radius,
            self.radius,
            2,
            8,
            pr.BLACK
        )
