import pygame
from ui_element import UIElement

class Image(UIElement):
    """画像 UI コンポーネント"""
    def __init__(self, canvas, image_path, **kwargs):
        super().__init__(canvas, **kwargs)
        self.image = pygame.image.load(image_path).convert_alpha()
        self.update_transform()

    def update_transform(self):
        """スケールと位置を適用"""
        self.transformed_image = pygame.transform.scale(self.image, self.size)

    def render(self, screen):
        """画像を描画"""
        if self.visible:
            position = self.get_position()
            screen.blit(self.transformed_image, position)
