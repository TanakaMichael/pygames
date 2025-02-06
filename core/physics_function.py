import math
import pygame
from core.component.transform import Transform

# ------------------------------
# 衝突マニフォールドを格納するクラス
# ------------------------------
class CollisionManifold:
    def __init__(self, penetration, normal, contact_point):
        self.penetration = penetration      # 浸透深さ
        self.normal = normal                # 衝突面の法線（衝突解決の方向）
        self.contact_point = contact_point  # 衝突接触点

# ------------------------------
# 衝突判定・マニフォールド計算関数
# ------------------------------

# 円 vs 円 の衝突マニフォールド計算
def circle_vs_circle_manifold(c1, c2):
    transform1 = c1.game_object.get_component(Transform)
    transform2 = c2.game_object.get_component(Transform)
    pos1 = transform1.get_global_position()
    pos2 = transform2.get_global_position()
    delta = pos2 - pos1
    dist = delta.length()
    sum_radii = c1.radius + c2.radius

    if dist == 0:
        # ２つの円の中心が一致している場合（非常に特殊な状況）には、任意の方向を設定
        normal = pygame.Vector2(1, 0)
        penetration = sum_radii
        contact_point = pos1
        return CollisionManifold(penetration, normal, contact_point)
    if dist >= sum_radii:
        return None  # 衝突していない

    penetration = sum_radii - dist
    normal = delta.normalize()
    # 接触点は円の境界上の点（pos1 から c1.radius 進んだ位置）とする
    contact_point = pos1 + normal * c1.radius
    return CollisionManifold(penetration, normal, contact_point)

# 矩形 vs 矩形 の衝突マニフォールド計算（AABB として扱う）
def box_vs_box_manifold(b1, b2):
    pos1 = b1.game_object.transform.get_global_position()  # ※ Transform は game_object 経由で取得済みである前提
    pos2 = b2.game_object.transform.get_global_position()
    # 右下の座標を計算
    r1 = pygame.Vector2(pos1.x + b1.width, pos1.y + b1.height)
    r2 = pygame.Vector2(pos2.x + b2.width, pos2.y + b2.height)
    
    overlap_x = min(r1.x, r2.x) - max(pos1.x, pos2.x)
    overlap_y = min(r1.y, r2.y) - max(pos1.y, pos2.y)
    if overlap_x <= 0 or overlap_y <= 0:
        return None  # 衝突していない

    # どちらの軸方向の重なりが小さいかで、法線方向を決定する
    if overlap_x < overlap_y:
        if pos1.x < pos2.x:
            normal = pygame.Vector2(-1, 0)
        else:
            normal = pygame.Vector2(1, 0)
        penetration = overlap_x
    else:
        if pos1.y < pos2.y:
            normal = pygame.Vector2(0, -1)
        else:
            normal = pygame.Vector2(0, 1)
        penetration = overlap_y

    # 接触点は重なっている領域の中心を採用
    contact_point = pygame.Vector2(
        (max(pos1.x, pos2.x) + min(r1.x, r2.x)) / 2,
        (max(pos1.y, pos2.y) + min(r1.y, r2.y)) / 2
    )
    return CollisionManifold(penetration, normal, contact_point)

# 矩形 vs 円 の衝突マニフォールド計算
def box_vs_circle_manifold(box, circle):
    rect_pos = box.game_object.transform.get_global_position()
    circle_pos = circle.game_object.transform.get_global_position()
    # 円の中心に最も近い矩形上の点を求める
    closest_x = max(rect_pos.x, min(circle_pos.x, rect_pos.x + box.width))
    closest_y = max(rect_pos.y, min(circle_pos.y, rect_pos.y + box.height))
    closest_point = pygame.Vector2(closest_x, closest_y)
    delta = circle_pos - closest_point
    dist = delta.length()
    if dist > circle.radius:
        return None  # 衝突していない
    if dist == 0:
        normal = pygame.Vector2(1, 0)
        penetration = circle.radius
        contact_point = closest_point
    else:
        normal = delta.normalize()
        penetration = circle.radius - dist
        contact_point = closest_point
    return CollisionManifold(penetration, normal, contact_point)

# 各コライダー間の衝突マニフォールドを計算するディスパッチ関数
def compute_collision_manifold(collider1, collider2):
    # インポートは相互参照に注意
    from core.component.physics.circle_collider import CircleCollider
    from core.component.physics.box_collider import BoxCollider

    if isinstance(collider1, CircleCollider) and isinstance(collider2, CircleCollider):
        return circle_vs_circle_manifold(collider1, collider2)
    elif isinstance(collider1, BoxCollider) and isinstance(collider2, BoxCollider):
        return box_vs_box_manifold(collider1, collider2)
    elif isinstance(collider1, BoxCollider) and isinstance(collider2, CircleCollider):
        return box_vs_circle_manifold(collider1, collider2)
    elif isinstance(collider1, CircleCollider) and isinstance(collider2, BoxCollider):
        manifold = box_vs_circle_manifold(collider2, collider1)
        if manifold is not None:
            manifold.normal = -manifold.normal  # 逆方向にする
        return manifold
    return None

