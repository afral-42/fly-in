import pyray as pr


class Camera:
    def __init__(
        self,
        up: pr.Vector3,
        fov: float,
        projection: pr.CameraProjection,
        target: pr.Vector3,
        position: pr.Vector3,
    ) -> None:
        self.camera = pr.Camera3D()
        self.camera.up = up
        self.camera.fovy = fov
        self.camera.projection = projection
        self.camera.target = target
        self.camera.position = position

    def switch_to_perspective(self) -> None:
        self.camera.projection = pr.CameraProjection.CAMERA_PERSPECTIVE

    def switch_to_orthographic(self) -> None:
        self.camera.projection = pr.CameraProjection.CAMERA_ORTHOGRAPHIC

    def begin_3d(self) -> None:
        pr.begin_mode_3d(self.camera)

    def end_3d(self) -> None:
        pr.end_mode_3d()
