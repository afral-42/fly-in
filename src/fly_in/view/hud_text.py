import pyray as pr
from fly_in.models.hud_text import HudTextModel


class HudTextView:
    def __init__(self) -> None:
        pass

    def render(self, text_model: HudTextModel) -> None:
        pr.draw_text(
            text_model.text,
            text_model.position_x,
            text_model.position_y,
            text_model.font_size,
            text_model.color
        )
