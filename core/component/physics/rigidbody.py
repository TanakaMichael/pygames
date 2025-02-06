import pygame
import math
from core.component.component import Component
class PhysicsMaterial:
    """
    物理マテリアル: 衝突時の反発係数と摩擦係数を定義するクラス
    """
    def __init__(self, friction=0.5, restitution=0.5):
        """
        :param friction: 摩擦係数 (0: 完全滑らか, 1: 高摩擦)
        :param restitution: 反発係数 (0: 完全非弾性, 1: 完全弾性)
        """
        self.friction = max(0, min(friction, 1))         # 0〜1 の範囲に制限
        self.restitution = max(0, min(restitution, 1))   # 0〜1 の範囲に制限

class RigidBody(Component):
    """物理オブジェクト (重力・速度・衝突解決)"""
    STATIC = 0
    DYNAMIC = 1

    def __init__(self, game_object, mass=1, gravity=pygame.Vector2(0, 9.8), is_static=False, friction=0.5, restitution=0.5, def_on_collision_enter=None, def_on_collision_exit=None):
        super().__init__(game_object)
        self.mass = 0 if is_static else mass
        self.inv_mass = 0 if self.mass == 0 else 1 / self.mass  # **逆質量 (静的オブジェクトは 0)**
        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = pygame.Vector2(0, 0)
        self.gravity = gravity if not is_static else pygame.Vector2(0, 0)
        self.is_static = is_static
        self.physics_material = PhysicsMaterial(friction, restitution)
        self.max_speed = float('inf')  # **最大速度 (default: 無限)**
        self.def_on_collision_enter = def_on_collision_enter
        self.def_on_collision_exit = def_on_collision_exit
        # ✅ 衝突管理用のセット
        self.current_collisions = set()  # 今フレームで衝突しているオブジェクト
        self.previous_collisions = set()  # 前フレームで衝突していたオブジェクト
    def on_collision_enter(self, other):
        """コールバック (オプション)"""
        if self.def_on_collision_enter is not None:
            self.def_on_collision_enter(other)
    def on_collision_exit(self, other):
        """コールバック (オプション)"""
        if self.def_on_collision_exit is not None:
            self.def_on_collision_exit(other)
    def apply_force(self, force):
        """オブジェクトに力を加える"""
        if not self.is_static:
            self.acceleration += force * self.inv_mass
    def check_collision_events(self):
        """衝突開始・終了イベントを検知"""
        # ✅ 衝突終了を検出
        for obj in self.previous_collisions - self.current_collisions:
            self.on_collision_exit(obj)

        # ✅ 衝突開始を検出
        for obj in self.current_collisions - self.previous_collisions:
            self.on_collision_enter(obj)

        # 衝突情報を更新
        self.previous_collisions = self.current_collisions.copy()
        self.current_collisions.clear()
    def apply_move_force(self, move_force, max_speed):
        """
        **移動用の力を加える (最大速度制限付き)**  
        `move_force`: 移動させたい方向への力 (ベクトル)
        **現在の速度が `max_speed` 未満の場合のみ** 力を加える
        """
        self.max_speed = max_speed
        if not self.is_static:
            current_speed = self.velocity.length()

            # **最大速度未満なら力を加える**
            if current_speed < self.max_speed:
                self.apply_force(move_force)

    def update(self, delta_time):
        """物理計算 (速度・位置更新)"""
        if self.is_static:
            return  # **静的オブジェクトは動かない**

        # **重力適用**
        self.velocity += self.gravity * delta_time
        self.velocity += self.acceleration * delta_time
        self.game_object.transform.local_position += self.velocity * delta_time
        self.acceleration = pygame.Vector2(0, 0)  # **加速度リセット**