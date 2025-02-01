import random
from core.network.network_game_object import NetworkGameObject
from core.network.network_object_factory import NetworkObjectFactory
from core.network.network_manager import NetworkManager
from core.game_scene_manager import GameSceneManager
from SnakeGame.food import Food
import pygame
class FoodManager(NetworkGameObject):
    """フード (エサ) を管理"""

    def __init__(self, steam_id=-1, network_id=None):
        super().__init__("FoodManager", steam_id=steam_id, network_id=network_id)
        if NetworkManager.get_instance().is_server:
            self.spawn_food()
            self.network_manager.add_network_object(self)

    def spawn_food(self):
        """ランダムな位置にフードを生成"""
        for _ in range(10):
            x = random.randint(100, 1800)
            y = random.randint(100, 900)
            food = Food(position=pygame.Vector2(x, y))
            GameSceneManager.get_instance().current_scene.spawn_object(food)

# **自動で NetworkObjectFactory に登録**
NetworkObjectFactory.register_class(FoodManager)