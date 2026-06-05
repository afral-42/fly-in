import pyray as pr

from fly_in.models.world import WorldModel
from fly_in.view.world import WorldView


class ControllerError(Exception):
    pass


class WorldController:
    def __init__(self, view: WorldView, model: WorldModel) -> None:
        self.view = view
        self.model = model
        self.animation = False

    def loop(self) -> None:
        while not pr.window_should_close():
            if pr.is_key_pressed(pr.KeyboardKey.KEY_SPACE):
                self.animation = not self.animation

            if self.animation or pr.is_key_pressed(pr.KeyboardKey.KEY_RIGHT):
                self.model.start_animation()

            move_z = 0.0
            move_q = 0.0

            if pr.is_key_down(pr.KeyboardKey.KEY_W):
                move_z += 1.0
            if pr.is_key_down(pr.KeyboardKey.KEY_S):
                move_z -= 1.0
            if pr.is_key_down(pr.KeyboardKey.KEY_A):
                move_q -= 1.0
            if pr.is_key_down(pr.KeyboardKey.KEY_D):
                move_q += 1.0

            if move_z != 0.0 or move_q != 0.0:
                self.view.move_camera_zqsd(move_z, move_q)

            if pr.is_key_pressed(pr.KeyboardKey.KEY_UP):
                self.model.increase_speed()

            if pr.is_key_pressed(pr.KeyboardKey.KEY_DOWN):
                self.model.decrease_speed()

            self.model.update_state()
            self.view.render(self.model)
