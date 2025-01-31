import random
from core.network.network_game_object import NetworkGameObject
from core.network.network_object_factory import NetworkObjectFactory
from core.network.network_manager import NetworkManager
from core.game_scene_manager import GameSceneManager
from SnakeGame.food import Food

class FoodManager(NetworkGameObject):
    """フード (エサ) を管理"""

    def __init__(self):
        super().__init__("FoodManager")
        if NetworkManager.get_instance().is_server:
            self.spawn_food()

    def spawn_food(self):
        """ランダムな位置にフードを生成"""
        for _ in range(10):
            x = random.randint(100, 1800)
            y = random.randint(100, 900)
            food = Food(x, y)
            GameSceneManager.get_instance().current_scene.spawn_object(food)

# **自動で NetworkObjectFactory に登録**
NetworkObjectFactory.register_class(Food)