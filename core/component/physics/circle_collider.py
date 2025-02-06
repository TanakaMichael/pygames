from core.component.physics.collider import Collider
from core.component.transform import Transform
from math import sqrt
import pygame
class CircleCollider(Collider):
    """円のコライダー"""
    def __init__(self, game_object, radius, offset=pygame.Vector2(0, 0)):
        super().__init__(game_object)
        self.radius = radius
        self.offset = offset  # **ローカル座標でのオフセット**

    def get_center(self):
        """円の中心座標を取得"""
        return self.game_object.transform.global_position + self.offset
