from core.component.physics.circle_collider import CircleCollider
from core.component.sprite import Sprite
from core.game_object import GameObject
from core.input_manager import InputManager
from core.camera import Camera

from core.component.physics.rigidbody import RigidBody
import pygame

class Player(GameObject):
    def __init__(self, visible=True, camera=None):
        super().__init__("Player", visible)
        self.movement_speed = 500

        self.max_speed = 2000
        #self.rigidbody = self.add_component(RigidBody, gravity=pygame.Vector2(0,0))
        #self.collider = self.add_component(CircleCollider, radius=50)
        self.sprite = self.add_component(Sprite, image_path="SnakeGame/assets/snake.png", base_size=(100, 100))
        self.transform.set_local_position(pygame.Vector2(200, 0))
        camera.set_target(self)
        self.input_manager = InputManager.get_instance()
        self.input_manager.register_event("MoveUp", self.move_up, "on_press")
        self.input_manager.register_event("MoveDown", self.move_down, "on_press")
        self.input_manager.register_event("MoveLeft", self.move_left, "on_press")
        self.input_manager.register_event("MoveRight", self.move_right, "on_press")
    def start(self):
        self.camera = self.scene.add_camera(Camera(self.scene.canvas))
        self.camera.set_target(self)

    def move_up(self):
        self.collider.rigid_body.apply_move_force(pygame.Vector2(0, -self.movement_speed), self.max_speed)
    def move_down(self):
        self.collider.rigid_body.apply_move_force(pygame.Vector2(0, self.movement_speed), self.max_speed)
    def move_left(self):
        self.collider.rigid_body.apply_move_force(pygame.Vector2(-self.movement_speed, 0), self.max_speed)
    def move_right(self):
        self.collider.rigid_body.apply_move_force(pygame.Vector2(self.movement_speed, 0), self.max_speed)