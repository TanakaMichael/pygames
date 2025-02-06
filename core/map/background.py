import pygame
from core.map.layer import Layer  # Layerの基底クラスを継承

class Background(Layer):
    def __init__(self, name, image_path, parallax_factor=0.5, loop_x=True, loop_y=False):
        super().__init__(name, parallax_factor)
        self.image = pygame.image.load(image_path).convert_alpha()
        self.loop_x = loop_x  # ⬅️➡️ 横方向ループ
        self.loop_y = loop_y  # ⬆️⬇️ 縦方向ループ
        self.image_size = pygame.Vector2(self.image.get_size())

    def render(self, surface, camera):
        if not self.visible:
            return

        camera_pos = camera.transform.local_position
        parallax_offset = camera_pos * (1 - self.parallax_factor)

        # ✅ カメラの描画範囲を取得
        view_rect = camera.view_canvas_size
        screen_size = pygame.Vector2(view_rect.size)

        # ✅ 背景画像をどこに描画するか決定
        start_x = - (parallax_offset.x % self.image_size.x) if self.loop_x else 0
        start_y = - (parallax_offset.y % self.image_size.y) if self.loop_y else 0

        # ✅ 背景を繰り返して描画
        x = start_x
        while x < screen_size.x:
            y = start_y
            while y < screen_size.y:
                surface.blit(self.image, (x, y))
                if not self.loop_y:
                    break
                y += self.image_size.y
            if not self.loop_x:
                break
            x += self.image_size.x
