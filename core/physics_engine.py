from core.component.physics.rigidbody import RigidBody
from core.component.physics.collider import Collider
from core.component.physics.rigidbody import RigidBody

from core.physics_function import compute_collision_manifold
import pygame
import math
from core.component.transform import Transform

# ------------------------------
# 衝突解決（インパルス解法＋摩擦＋位置補正）
# ------------------------------
def resolve_collision(manifold, collider1, collider2):
    obj1 = collider1.game_object
    obj2 = collider2.game_object

    rb1 = obj1.get_component(RigidBody)
    rb2 = obj2.get_component(RigidBody)

    if rb1 is None or rb2 is None:
        return

    relative_velocity = rb2.velocity - rb1.velocity
    vel_along_normal = relative_velocity.dot(manifold.normal)
    if vel_along_normal > 0:
        return  # すでに分離している場合は解決不要

    # ✅ 衝突中のオブジェクトとして登録
    rb1.current_collisions.add(rb2)
    rb2.current_collisions.add(rb1)

    # **反発係数 (restitution) 計算**
    restitution = min(rb1.physics_material.restitution, rb2.physics_material.restitution)
    impulse_scalar = -(1 + restitution) * vel_along_normal
    impulse_scalar /= (rb1.inv_mass + rb2.inv_mass)
    impulse = manifold.normal * impulse_scalar

    # **衝突インパルス適用**
    rb1.velocity -= impulse * rb1.inv_mass
    rb2.velocity += impulse * rb2.inv_mass

    # **位置補正**
    percent = 0.8
    slop = 0.01
    correction_magnitude = max(manifold.penetration - slop, 0) / (rb1.inv_mass + rb2.inv_mass) * percent
    correction = manifold.normal * correction_magnitude
    obj1.transform.local_position -= correction * rb1.inv_mass
    obj2.transform.local_position += correction * rb2.inv_mass

class PhysicsEngine:
    """ゲームシーンに統合された物理エンジン"""
    def __init__(self):
        self.rigidbodies = []  # RigidBody を持つオブジェクト
        self.colliders = []    # Collider を持つオブジェクト

    def update_scene(self, objects):
        """シーン内のすべてのオブジェクトから Rigidbody と Collider を自動検出"""
        self.rigidbodies.clear()
        self.colliders.clear()

        for obj in objects:
            # **Rigidbody の登録**
            rb = obj.get_component(RigidBody)
            if rb:
                self.rigidbodies.append(rb)

            # **Collider の登録**
            col = obj.get_component(Collider)
            if col:
                self.colliders.append(col)

    def update(self, delta_time):
        """物理エンジンの更新 (重力・衝突処理)"""
        # **衝突判定と解決**
        self.resolve_collisions()
        # ✅ 衝突イベントの更新
        for rb in self.rigidbodies:
            rb.check_collision_events()

    def resolve_collisions(self):
        """全コライダー間の衝突判定と解決"""
        num = len(self.colliders)
        for i in range(num):
            for j in range(i + 1, num):
                col1 = self.colliders[i]
                col2 = self.colliders[j]
                manifold = compute_collision_manifold(col1, col2)
                if manifold:
                    resolve_collision(manifold, col1, col2)