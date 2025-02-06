import pygame
from core.component.component import Component
from core.component.physics.rigidbody import RigidBody
from core.input_manager import InputManager
from core.network.network_manager import NetworkManager
from core.component.transform import Transform

class SnakeMovement(Component):
    """スネークの移動を管理"""
    def __init__(self, game_object, speed=2000):
        super().__init__(game_object)
        self.speed = speed
        self.direction = pygame.Vector2(1, 0)  # **初期方向は右**
        # **RigidBody の取得**
        self.rigidbody = game_object.add_component(RigidBody)
        self.transform = game_object.get_component(Transform)

        if not self.transform:
            raise ValueError("SnakeMovement は Transform コンポーネントを必要とします")

        # **InputManager の取得**
        self.input_manager = InputManager.get_instance()
        self.network_manager = NetworkManager.get_instance()
        if not game_object.is_local_player and not self.network_manager.is_server:
            return
        # **キー入力イベントを登録**
        self.input_manager.register_server_event("MoveUp", self.move_up, game_object.steam_id)
        self.input_manager.register_server_event("MoveDown", self.move_down, game_object.steam_id)
        self.input_manager.register_server_event("MoveLeft", self.move_left, game_object.steam_id)
        self.input_manager.register_server_event("MoveRight", self.move_right, game_object.steam_id)

    def move_up(self):
        """上方向に移動"""
        if self.direction.y == 0:  # **逆走を防ぐ**
            self.direction = pygame.Vector2(0, -1)

    def move_down(self):
        """下方向に移動"""
        if self.direction.y == 0:
            self.direction = pygame.Vector2(0, 1)

    def move_left(self):
        """左方向に移動"""
        if self.direction.x == 0:
            self.direction = pygame.Vector2(-1, 0)

    def move_right(self):
        """右方向に移動"""
        if self.direction.x == 0:
            self.direction = pygame.Vector2(1, 0)

    def update(self, delta_time):
        """スネークを現在の方向に移動"""
        super().update(delta_time)
        if self.network_manager.is_server:
            move_amount = self.direction * self.speed * delta_time
            self.rigidbody.apply_velocity(move_amount)
