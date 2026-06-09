import pyray as pr


class HudTextModel:
    def __init__(
        self,
        text: str,
        position_x: int,
        position_y: int,
        font_size: int,
        color: pr.Color
    ) -> None:
        self.text = text
        self.position_x, self.position_y = position_x, position_y
        self.color = color
        self.font_size = font_size
