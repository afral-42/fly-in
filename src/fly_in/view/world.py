import pyray as pr
from pathlib import Path
from types import TracebackType
from typing import Self

from fly_in.models.world import WorldModel
from fly_in.view.camera import Camera
from fly_in.view.connection import ConnectionView
from fly_in.view.drone import DroneView
from fly_in.view.hub import HubView
from fly_in.view.text import TextView


class WorldView:
    def __init__(self) -> None:
        self.camera = Camera(
            up=pr.Vector3(0.0, 1.0, 0.0),
            fov=45.0,
            projection=pr.CameraProjection(
                pr.CameraProjection.CAMERA_PERSPECTIVE
            ),
            target=pr.Vector3(0.0, 0.0, 0.0),
            position=pr.Vector3(0.0, 40.0, 50.0)
        )

        package_dir = Path(__file__).resolve().parent.parent
        self.model_path = str(package_dir / "assets" / "dji_spark.glb")
        self.font_path = str(package_dir / "assets" / "superstar_memesbruh03.ttf")

    def __enter__(self) -> Self:
        self.drone_model = pr.load_model(self.model_path)
        self.drone_view = DroneView(
            self.drone_model
        )
        self.font_model = pr.load_font_ex(self.font_path, 96, None, 0)
        self.hub_view = HubView()
        self.connection_view = ConnectionView()
        self.text_view = TextView(self.font_model)

        return self

    def __exit__(
        self, 
        exc_type: type[BaseException] | None, 
        exc_val: BaseException | None, 
        exc_tb: TracebackType | None
    ) -> None:
        pr.unload_model(self.drone_model)

    def center_camera(self, world_model: WorldModel) -> None:
        xs = [hub.position.x for hub in world_model.hubs.values()]
        ys = [hub.position.z for hub in world_model.hubs.values()]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        center_x = (min_x + max_x) / 2.0
        center_y = (min_y + max_y) / 2.0

        target_x = center_x
        target_z = center_y

        map_size = max(max_x - min_x, max_y - min_y)
        
        camera_height = map_size * 0.8 
        camera_distance = map_size * 0.8
        self.camera.camera.target = pr.Vector3(target_x, 0.0, target_z)
        self.camera.camera.position = pr.Vector3(target_x, camera_height, target_z + camera_distance)
        
    def render(self, world: WorldModel) -> None:
        pr.begin_drawing()
        back_color = pr.Color(251, 240, 233, 255)
        pr.clear_background(back_color)   
        self.camera.begin_3d()
        for drone in world.drones:
            self.drone_view.render(drone)

        for hub in world.hubs.values():
            self.hub_view.render(hub)
        
        for connection in world.connections:
            self.connection_view.render(connection)

        for text in world.texts:
            self.text_view.render(text)

        self.camera.end_3d()
        pr.end_drawing()
