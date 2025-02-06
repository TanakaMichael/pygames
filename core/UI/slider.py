import pygame
from core.UI.elements.image import Image

class Slider:
    """スライダー UI コンポーネント"""
    def __init__(self, canvas, position=(0.5, 0.5), size=(200, 30), min_value=0, max_value=1, initial_value=0.5):
        self.canvas = canvas
        self.position = position
        self.size = size
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value

        self.handle_path = None
        self.bar_path = None

        # **スライダーの背景 (バー)**
        self.bar = Image(canvas, self.bar_path, anchor=self.position, size=self.size, layer=0)

        # **スライダーのハンドル**
        handle_size = (size[1], size[1])  # **高さを基準に正方形のハンドル**
        self.handle = Image(canvas, self.handle_path, anchor=self.position, size=handle_size, layer=1)

        self.dragging = False

    def update(self, delta_time):
        """スライダーの更新 (マウス操作を処理)"""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()[0]

        # **マウスがハンドルの上にあるかチェック**
        handle_x, handle_y = self.handle.get_position()
        handle_w, handle_h = self.handle.size
        if handle_x <= mouse_x <= handle_x + handle_w and handle_y <= mouse_y <= handle_y + handle_h:
            if click:
                self.dragging = True

        if not click:
            self.dragging = False

        if self.dragging:
            # **スライダーの値を計算**
            bar_x, _ = self.bar.get_position()
            self.value = (mouse_x - bar_x) / self.size[0]
            self.value = max(self.min_value, min(self.max_value, self.value))

            # **ハンドルの位置を更新**
            self.handle.anchor = (self.position[0] - 0.5 + self.value, self.position[1])
            self.handle.update_transform()

    def render(self, screen):
        """スライダーの描画"""
        self.bar.render(screen)
        self.handle.render(screen)
