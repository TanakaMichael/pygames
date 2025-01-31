from core.game_scene import GameScene
from SnakeGame.food_manager import FoodManager
from SnakeGame.game_manager import GameManager
from SnakeGame.snake import Snake
from core.network.network_manager import NetworkManager
class SnakeGameScene(GameScene):
    def __init__(self, name, screen):
        super().__init__(name, screen)
        self.network_manager = NetworkManager.get_instance()
    def start(self):
        super().start()
        if self.network_manager.is_server:
            self.add_object(Snake(f"Player_{self.network_manager.server_id}", steam_id=self.network_manager.server_id))
        self.add_object(FoodManager())
        self.add_object(GameManager())

    def update(self, delta_time):
        super().update(delta_time)