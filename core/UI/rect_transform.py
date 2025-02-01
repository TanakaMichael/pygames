# ファイル: core/ui/rect_transform.py
import pygame
class RectTransform:
    def __init__(self, anchor=pygame.Vector2(0.5, 0.5), size=pygame.Vector2(1, 1), position=pygame.Vector2(200, 200)):
        """
        :param anchor: (0.0〜1.0) の値で画面上の位置を指定（anchor モードの場合）
        :param size: (幅, 高さ)
        :param position: 絶対位置（absolute モードの場合）
        """
        self.anchor = anchor
        self.size = size
        self.position = position

    def get_calculated_position(self, canvas_size, mode="anchor"):
        """
        :param canvas_size: (幅, 高さ) のタプル
        :param mode: "anchor" ならアンカー計算、"absolute" なら絶対座標を返す
        :return: 描画位置 (x, y)
        """
        if mode == "anchor":
            x = int(self.anchor.x * canvas_size[0] - self.size.x / 2)
            y = int(self.anchor.y * canvas_size[1] - self.size.y / 2)
            return pygame.Vector2(x, y)
        elif mode == "absolute":
            return self.position
        else:
            return pygame.Vector2(0, 0)
