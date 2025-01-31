import pygame
from ui_element import UIElement

class Text(UIElement):
    """テキスト UI コンポーネント"""
    def __init__(self, canvas, text, font_size=30, font_color=(255, 255, 255), **kwargs):
        super().__init__(canvas, **kwargs)
        self.text = text
        self.font = pygame.font.Font(None, font_size)
        self.font_color = font_color

    def render(self, screen):
        """テキストを描画"""
        if self.visible:
            position = self.get_position()
            text_surface = self.font.render(self.text, True, self.font_color)
            screen.blit(text_surface, position)
