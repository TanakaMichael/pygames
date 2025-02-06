import pygame
from core.component.component import Component
from core.component.physics.rigidbody import RigidBody

class Collider(Component):
    """すべてのコライダーの基底クラス"""
    def __init__(self, game_object):
        super().__init__(game_object)
        self.rigid_body = game_object.get_component(RigidBody)  # **Rigidbody 参照**