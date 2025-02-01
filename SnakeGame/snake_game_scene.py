from core.game_scene import GameScene
from SnakeGame.food_manager import FoodManager
from SnakeGame.game_manager import GameManager
from SnakeGame.snake import Snake
from core.network.network_game_scene import NetworkGameScene
class SnakeGameScene(NetworkGameScene):
    def __init__(self, name, screen):
        super().__init__(name, screen)
    def start(self):
        super().start()
        if self.network_manager.is_server:
            self.add_object(Snake(name=f"Player_{self.network_manager.server_id}", steam_id=self.network_manager.server_id))
        self.add_object(FoodManager())
        self.add_object(GameManager())

    def update(self, delta_time):
        super().update(delta_time)