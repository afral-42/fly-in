import pyray as pr

from fly_in.models.hub import HubModel


class HubView:
    def __init__(
        self,
    ) -> None:
        pass

    def render(self, hub: HubModel) -> None:
        pr.draw_cylinder(
            hub.position,
            hub.radius,
            hub.radius,
            hub.height,
            hub.slices,
            hub.color
        )
        pr.draw_cylinder_wires(
            hub.position,
            hub.radius,
            hub.radius,
            hub.height,
            hub.slices,
            pr.BLACK
        )
