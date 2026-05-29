import pyray as pr
from fly_in.models.text import TextModel


class TextView:
    def __init__(self, font_model: pr.Font) -> None:
        self.model = font_model
        self.cache: dict[str, pr.Model] = {}

    def render(self, text_model: TextModel) -> None:
        if text_model.text in self.cache:
            pr.draw_model(
                self.cache[text_model.text], 
                text_model.position, 
                1.0, 
                pr.WHITE
            )
            return

        img = pr.image_text_ex(
            self.model,
            text_model.text,
            96,
            0,
            pr.BLACK
        )

        texture = pr.load_texture_from_image(img)
        aspect_ratio = img.width / img.height

        height = text_model.size
        width = height * aspect_ratio

        mesh = pr.gen_mesh_plane(width, height, 1, 1)
        model = pr.load_model_from_mesh(mesh)

        model.materials[0].maps[pr.MATERIAL_MAP_DIFFUSE].texture = texture
        self.cache[text_model.text] = model
        pr.rl_disable_depth_mask()
        pr.draw_model(
            model, 
            text_model.position, 
            1.0, 
            pr.WHITE
        )
        pr.rl_enable_depth_mask()        
