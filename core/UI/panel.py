import pygame
from .ui_element import UIElement

class Panel(UIElement):
    """UI のコンテナや背景として使用するパネル"""
    def __init__(self, canvas, anchor=(0.5, 0.5), size=(200, 100), position_mode="anchor", color=(50, 50, 50), layer=0):
        super().__init__(canvas, anchor, size, position_mode, color, layer)

    def render(self, screen):
        """パネルを描画"""
        if self.visible:
            position = self.get_position()
            pygame.draw.rect(screen, self.color, (*position, *self.size))
