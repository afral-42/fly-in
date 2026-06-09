import pyray as pr


class ConnectionModel:
    def __init__(
        self, start: pr.Vector3, end: pr.Vector3, color: pr.Color = pr.BLACK
    ) -> None:
        """Model representing a visual connection between two points.

        Args:
            start: 3D start position.
            end: 3D end position.
            color: Optional color for the connection rendering.
        """
        self.start = start
        self.end = end
        self.start.y += 1
        self.end.y += 1
        self.color = color
