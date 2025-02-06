import pygame
import random
from core.coroutine import WaitForSeconds
from core.UI.component.UIAnimation import UIAnimation

class GridRevealAnimation(UIAnimation):
    def __init__(self, ui_object, grid_size=(5, 5), duration=2.0):
        super().__init__(ui_object)
        self.grid_size = grid_size
        self.duration = duration
        self.cell_alpha = {}  # 各セルの透過度

        self._generate_grid()

    def _generate_grid(self):
        """グリッドの初期化"""
        width, height = self.ui_object.get_canvas_size()
        cols, rows = self.grid_size
        cell_width = width / cols
        cell_height = height / rows

        for col in range(cols):
            for row in range(rows):
                delay = random.uniform(0, self.duration * 0.8)
                self.cell_alpha[(col, row)] = {"alpha": 0, "delay": delay}

    def start_fade_in(self):
        """フェードイン開始"""
        for key in self.cell_alpha:
            self.cell_alpha[key]["alpha"] = 0  # 初期化
        super().start_animation(self.reveal_animation)

    def start_fade_out(self):
        """フェードアウト開始"""
        for key in self.cell_alpha:
            self.cell_alpha[key]["alpha"] = 255  # 初期化
        super().start_animation(self.fade_out_animation)

    def reveal_animation(self):
        """フェードインアニメーション"""
        elapsed = 0
        while elapsed < self.duration:
            delta_time = yield WaitForSeconds(0.01)
            elapsed += delta_time

            for (col, row), data in self.cell_alpha.items():
                delay = data["delay"]
                if elapsed > delay:
                    progress = min(1, (elapsed - delay) / (self.duration - delay))
                    self.cell_alpha[(col, row)]["alpha"] = int(255 * progress)

    def fade_out_animation(self):
        """フェードアウトアニメーション"""
        elapsed = 0
        while elapsed < self.duration:
            delta_time = yield WaitForSeconds(0.01)
            elapsed += delta_time

            for (col, row), data in self.cell_alpha.items():
                delay = data["delay"]
                if elapsed > delay:
                    progress = min(1, (elapsed - delay) / (self.duration - delay))
                    self.cell_alpha[(col, row)]["alpha"] = int(255 * (1 - progress))

    def render(self, screen):
        """描画処理"""
        width, height = self.ui_object.get_canvas_size()
        cols, rows = self.grid_size
        cell_width = width / cols
        cell_height = height / rows

        pos = self.ui_object.rect_transform.local_position
        scale_factor = self.ui_object.canvas.get_scale_factor()

        for (col, row), data in self.cell_alpha.items():
            alpha = data["alpha"]
            color = pygame.Color(0, 0, 0, alpha)

            screen_x = (pos.x - width / 2) * scale_factor.x + col * cell_width
            screen_y = (pos.y - height / 2) * scale_factor.y + row * cell_height

            cell_rect = pygame.Rect(screen_x, screen_y, cell_width, cell_height)
            pygame.draw.rect(screen, color, cell_rect)
