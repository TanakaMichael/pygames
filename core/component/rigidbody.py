import pygame
from core.component.component import Component
from core.component.transform import Transform
from core.component.physics_material import PhysicsMaterial
from core.network.network_manager import NetworkManager

class RigidBody(Component):
    """物理演算を行う RigidBody"""
    STATIC = "static"
    DYNAMIC = "dynamic"
    KINEMATIC = "kinematic"

    def __init__(self, game_object, mass=1.0, gravity=0, friction=0.98, collision_response=DYNAMIC, physics_material=None):
        super().__init__(game_object)
        self.mass = mass
        self.gravity = gravity  # **重力**
        self.velocity = pygame.Vector2(0, 0)  # **速度**
        self.acceleration = pygame.Vector2(0, 0)  # **加速度**
        self.collision_response = collision_response  # **衝突オプション**
        self.transform = game_object.get_component(Transform)
        self.physics_material = physics_material or PhysicsMaterial(friction, 0.5)
        self.network_manager = NetworkManager.get_instance()


        if not self.transform:
            raise ValueError("RigidBody は Transform コンポーネントを必要とします")

    def apply_force(self, force):
        """外部からの力を適用"""
        if self.collision_response == RigidBody.DYNAMIC:
            self.acceleration += force / self.mass

    def update(self, delta_time):
        """サーバーでのみ物理計算を行う"""
        super().update(delta_time)
        if self.network_manager.is_server and self.collision_response == RigidBody.DYNAMIC:
            self.apply_force(pygame.Vector2(0, self.gravity))  # **重力適用**
            self.velocity += self.acceleration * delta_time
            self.velocity *= self.physics_material.friction  # **摩擦の適用**
            self.transform.position += self.velocity * delta_time  # **位置更新**
            self.acceleration = pygame.Vector2(0, 0)  # **加速度リセット**
    def apply_velocity(self, velocity):
        """速度を適用"""
        self.velocity = velocity
