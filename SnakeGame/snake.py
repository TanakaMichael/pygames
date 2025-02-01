from core.game_object import GameObject
from core.network.network_game_object import NetworkGameObject
from core.network.network_object_factory import NetworkObjectFactory
from core.network.network_transform import NetworkTransform
from core.component.sprite import SpriteRenderer
from core.component.transform import Transform
from SnakeGame.snake_movement import SnakeMovement
from SnakeGame.snake_collider import SnakeCollider
from SnakeGame.player import Player
import pygame

class Snake(NetworkGameObject):
    """プレイヤーのスネーク"""
    def __init__(self, steam_id=-1, network_id=None, name=f"Snake"):
        super().__init__(name=name, steam_id=steam_id, network_id=network_id)
        # **スプライトの設定**
        self.transform = self.add_component(Transform, position=pygame.Vector2(500, 500))
        self.network_transform = self.add_component(NetworkTransform)
        self.sprite = self.add_component(SpriteRenderer, image_path="SnakeGame/assets/snake.png")
        
        # **移動と衝突処理の追加**
        self.movement = self.add_component(SnakeMovement)
        self.snake_collider = self.add_component(SnakeCollider, radius=16)

        # **スネークの全体処理を管理**
        self.player = self.add_component(Player)

    def update(self, delta_time):
        """スネークの更新処理"""
        super().update(delta_time)
    def render(self, screen):
        """スネークの描画処理"""
        super().render(screen)

# **自動で NetworkObjectFactory に登録**
NetworkObjectFactory.register_class(Snake)