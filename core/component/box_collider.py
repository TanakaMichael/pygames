from .collider import Collider
from .circle_collider import CircleCollider

class BoxCollider(Collider):
    """矩形の当たり判定 (2D)"""
    def __init__(self, owner, width, height):
        super().__init__(owner)
        self.width = width
        self.height = height

    def check_collision(self, other):
        """矩形 vs 矩形 & 矩形 vs 円の当たり判定"""
        super().update(0) # enabledの状態によってはチェックしない
        from .box_collider import BoxCollider
        from .circle_collider import CircleCollider

        if isinstance(other, BoxCollider):
            return self.rect_vs_rect(other)
        elif isinstance(other, CircleCollider):
            return self.rect_vs_circle(other)
        return False

    def rect_vs_rect(self, other):
        """矩形 vs 矩形 の当たり判定"""
        ax, ay = self.owner.transform.position
        bx, by = other.owner.transform.position
        return (
            ax < bx + other.width and ax + self.width > bx and
            ay < by + other.height and ay + self.height > by
        )

    def rect_vs_circle(self, circle):
        """矩形 vs 円 の当たり判定"""
        cx, cy = circle.owner.transform.position
        rx, ry = self.owner.transform.position
        closest_x = max(rx, min(cx, rx + self.width))
        closest_y = max(ry, min(cy, ry + self.height))
        distance_x = cx - closest_x
        distance_y = cy - closest_y
        return (distance_x**2 + distance_y**2) < (circle.radius**2)