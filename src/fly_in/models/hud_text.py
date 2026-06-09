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
        """Data container for HUD (2D overlay) text entries.

        Args:
            text: The string to render.
            position_x: X pixel coordinate.
            position_y: Y pixel coordinate.
            font_size: Size of the font to use.
            color: Color of the text.
        """
        self.text = text
        self.position_x, self.position_y = position_x, position_y
        self.color = color
        self.font_size = font_size
