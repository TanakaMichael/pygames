from .collider import Collider
from .circle_collider import CircleCollider
import pygame

class BoxCollider(Collider):
    """矩形 (AABB) のコライダー"""
    def __init__(self, game_object, width, height, offset=pygame.Vector2(0, 0)):
        super().__init__(game_object)
        self.width = width
        self.height = height
        self.offset = offset  # **ローカル座標でのオフセット**

    def get_bounds(self):
        """ボックスの AABB 境界を取得"""
        pos = self.game_object.transform.global_position + self.offset
        return pygame.Rect(pos.x, pos.y, self.width, self.height)
