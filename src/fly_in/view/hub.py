import pyray as pr

from fly_in.models.hub import HubModel


class HubView:
    def __init__(
        self,
    ) -> None:
        """View responsible for rendering `HubModel` instances."""

        pass

    def render(self, hub: HubModel) -> None:
        """Draw a hub as a filled cylinder with an outline.

        Args:
            hub: The `HubModel` instance to render.
        """
        pr.draw_cylinder(
            hub.position,
            hub.radius,
            hub.radius,
            hub.height,
            hub.slices,
            hub.color,
        )
        pr.draw_cylinder_wires(
            hub.position,
            hub.radius,
            hub.radius,
            hub.height,
            hub.slices,
            pr.BLACK,
        )
