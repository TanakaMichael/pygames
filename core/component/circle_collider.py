from core.component.collider import Collider
from math import sqrt

class CircleCollider(Collider):
    """円の当たり判定 (2D)"""
    def __init__(self, owner, radius):
        super().__init__(owner)
        self.radius = radius

    def check_collision(self, other):
        super().update(0)
        from .box_collider import BoxCollider
        from .circle_collider import CircleCollider

        if isinstance(other, CircleCollider):
            return self.circle_vs_circle(other)
        elif isinstance(other, BoxCollider):
            return other.rect_vs_circle(self)
        return False

    def circle_vs_circle(self, other):
        """円 vs 円 の当たり判定"""
        ax, ay = self.owner.transform.position
        bx, by = other.owner.transform.position
        distance = sqrt((ax - bx) ** 2 + (ay - by) ** 2)
        return distance < (self.radius + other.radius)
    