from core.component.physics.circle_collider import CircleCollider
from core.component.sprite import Sprite
from core.game_object import GameObject
from core.input_manager import InputManager
from core.component.physics.rigidbody import RigidBody
import pygame

class Box(GameObject):
    def __init__(self, visible=True):
        super().__init__("Player", visible)
        self.rigidbody = self.add_component(RigidBody, gravity=pygame.Vector2(0,0))
        self.collider = self.add_component(CircleCollider, radius=50)
        self.sprite = self.add_component(Sprite, image_path="SnakeGame/assets/food.png", base_size=(100, 100))
        self.transform.set_local_position(pygame.Vector2(0, 0))