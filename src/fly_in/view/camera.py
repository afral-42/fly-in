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
        """Wrapper around `pyray.Camera3D` to simplify usage.

        Args:
            up: Up vector for the camera.
            fov: Field of view in degrees.
            projection: Projection mode from `pyray.CameraProjection`.
            target: Camera target position.
            position: Camera position.
        """
        self.camera = pr.Camera3D()
        self.camera.up = up
        self.camera.fovy = fov
        self.camera.projection = projection
        self.camera.target = target
        self.camera.position = position

    def switch_to_perspective(self) -> None:
        """Set camera to perspective projection."""
        self.camera.projection = pr.CameraProjection.CAMERA_PERSPECTIVE

    def switch_to_orthographic(self) -> None:
        """Set camera to orthographic projection."""
        self.camera.projection = pr.CameraProjection.CAMERA_ORTHOGRAPHIC

    def begin_3d(self) -> None:
        """Enter 3D rendering mode using the internal camera."""
        pr.begin_mode_3d(self.camera)

    def end_3d(self) -> None:
        """Exit 3D rendering mode."""
        pr.end_mode_3d()
