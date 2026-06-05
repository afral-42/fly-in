import pyray as pr


class ConnectionModel:
    def __init__(
        self, start: pr.Vector3, end: pr.Vector3, color: pr.Color = pr.BLACK
    ) -> None:
        self.start = start
        self.end = end
        self.start.y += 1
        self.end.y += 1
        self.color = color
