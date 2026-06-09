import pyray as pr
from fly_in.models.text import TextModel

_MATERIAL_MAP_DIFFUSE = 0


class TextView:
    def __init__(self, font_model: pr.Font) -> None:
        """View that renders `TextModel` instances into textured planes.

        Args:
            font_model: Loaded `pyray.Font` used to rasterize text.
        """
        self.model = font_model
        self.cache: dict[
            tuple[str, pr.Color | None, pr.Color, float], pr.Model
        ] = {}

    def _cache_key(
        self, text_model: TextModel
    ) -> tuple[str, pr.Color | None, pr.Color, float]:
        """Return a hashable cache key for the provided `TextModel`."""
        return (
            text_model.text,
            text_model.background_color,
            text_model.color,
            text_model.size,
        )

    def render(self, text_model: TextModel) -> None:
        """Render or reuse a cached textured model for `text_model`.

        Args:
            text_model: The `TextModel` to render in the 3D scene.
        """
        cache_key = self._cache_key(text_model)
        if cache_key in self.cache:
            pr.draw_model(
                self.cache[cache_key],
                text_model.position,
                1.0,
                pr.WHITE,
            )
            return

        img = pr.image_text_ex(
            self.model, text_model.text, 96, 0, text_model.color
        )
        if text_model.background_color:
            pr.image_alpha_clear(img, text_model.background_color, 0.1)

        texture = pr.load_texture_from_image(img)
        aspect_ratio = img.width / img.height

        height = text_model.size
        width = height * aspect_ratio

        mesh = pr.gen_mesh_plane(width, height, 1, 1)
        model = pr.load_model_from_mesh(mesh)

        model.materials[0].maps[_MATERIAL_MAP_DIFFUSE].texture = texture
        self.cache[cache_key] = model
        pr.draw_model(model, text_model.position, 1.0, pr.WHITE)
