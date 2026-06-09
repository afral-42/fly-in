import pyray as pr


class TextModel:
    def __init__(
        self,
        text: str,
        position: pr.Vector3,
        background_color: pr.Color | None = None,
        size: float = 4.0,
        color: pr.Color = pr.BLACK,
    ) -> None:
        """Simple data holder for a 3D text element.

        Args:
            text: The string to display.
            position: 3D position for the text plane.
            background_color: Optional background clear color.
            size: Visual height of the text plane.
            color: Text color.
        """
        self.text = text
        self.position = position
        self.size = size
        self.color = color
        self.background_color = background_color
