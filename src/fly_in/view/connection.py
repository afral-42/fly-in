import pyray as pr

from fly_in.models.connection import ConnectionModel


class ConnectionView:
    def __init__(self) -> None:
        """View responsible for rendering `ConnectionModel` lines."""
        pass

    def render(self, connection: ConnectionModel) -> None:
        """Render a visual representation of a connection.

        Args:
            connection: `ConnectionModel` describing start and end.
        """
        pr.draw_line_3d(connection.start, connection.end, pr.BLACK)
        pr.draw_cylinder_ex(
            connection.start, connection.end, 0.3, 0.3, 1, connection.color
        )
