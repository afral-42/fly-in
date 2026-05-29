import pyray as pr

class TextModel:
    def __init__(
        self,
        text: str,
        position: pr.Vector3,
        background_color: pr.Color,
        size: float = 4.0,
        color: pr.Color = pr.DARKGRAY,
    ) -> None:
        self.text = text
        self.position = position
        self.size = size
        self.color = color
        self.background_color = background_color
