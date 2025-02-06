from core.UI.elements.text import Text
from core.UI.elements.image import Image
from core.UI.UIObject import UIObject
from core.UI.rect_transform import RectTransform
import pygame
class MeshImage(UIObject):
    def __init__(self, canvas, name="MeshImage", image_path=None,color=None, base_size=pygame.Vector2(100, 100), position=None,
                 rotation=None, visible=True):
        rect = RectTransform(canvas=canvas, position=position, rotation=rotation, is_child=True)
        super().__init__(canvas, name, rect, visible)
        local_rect = RectTransform(canvas=canvas, position=pygame.Vector2(0,0), rotation=rotation)
        self.image = self.add_element(Image(canvas, image_path, base_size, local_rect, color=color))
    def get_canvas_size(self):
        """最終的なMeshImageのキャンバス上のサイズを渡す"""
        scale = self.image.rect_transform.get_render_scale()
        return pygame.Vector2(self.base_size.x * scale.x, self.base_size.y * scale.y)