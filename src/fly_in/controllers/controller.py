import pyray as pr


from fly_in.models.world import WorldModel
from fly_in.view.world import WorldView

class ControllerError(Exception):
    pass


class WorldController:
    def __init__(self, view: WorldView, model: WorldModel) -> None:
        self.view = view
        self.model = model

    def loop(self):
        while not pr.window_should_close():
            if pr.is_key_pressed(pr.KEY_SPACE):
                self.model.start_animation()

            self.model.update_state()
            self.view.render(self.model)
