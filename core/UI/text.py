import pygame
from core.UI.ui_element import UIElement

class Text(UIElement):
    """テキスト UI コンポーネント"""
    def __init__(self, canvas, name="", text="", font_size=30, font_color=pygame.Color(255,255,255), position=pygame.Vector2(200,200),**kwargs):
        super().__init__(canvas,name,  **kwargs)

        self.text = text
        self.font = pygame.font.Font(None, font_size)
        self.font_color = font_color


    def render(self, screen):
        """テキストを描画"""
        if self.visible:
            position = self.get_position()
            text_surface = self.font.render(self.text, True, self.font_color)
            screen.blit(text_surface, position)
