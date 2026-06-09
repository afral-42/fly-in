import pyray as pr
from fly_in.models.hud_text import HudTextModel


class HudTextView:
    def __init__(self) -> None:
        """View to render 2D HUD text entries on the screen."""
        pass

    def render(self, text_model: HudTextModel) -> None:
        """Draw HUD text using `pyray.draw_text`.

        Args:
            text_model: `HudTextModel` containing text and position.
        """
        pr.draw_text(
            text_model.text,
            text_model.position_x,
            text_model.position_y,
            text_model.font_size,
            text_model.color,
        )
