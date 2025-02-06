from core.UI.elements.text import Text
from core.UI.UIObject import UIObject
from core.UI.rect_transform import RectTransform
import pygame
class MeshText(UIObject):
    def __init__(self, canvas, name="MeshText", font_path=None, text="", font_ratio=0.05, font_color=pygame.Color(255,255,255), position=pygame.Vector2(0,0),
                 rotation=0, visible=True):
        rect = RectTransform(canvas=canvas, local_position=position, local_rotation=rotation)
        super().__init__(canvas, name, rect, visible)
        local_rect = RectTransform(canvas=canvas, local_position=pygame.Vector2(0,0), local_rotation=rotation)
        self.text = self.add_element(Text(canvas, text, font_path, font_ratio, font_color, local_rect))
    def set_text(self, text):
        self.text.set_text(text)
    def get_text(self):
        return self.text.value
    def add_text(self, text):
        self.text.value += text
        self.text.set_text(self.text.value)
    def get_canvas_size(self):
        self.text.get_canvas_text_size()