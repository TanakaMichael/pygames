from .menu_objects.menu_panel import MenuPanel
from core.network.network_game_scene import NetworkGameScene
from SnakeGame.game_scene.menu_objects.join_server import JoinServer
from SnakeGame.game_scene.menu_objects.loading_server import LoadingServer

from SnakeGame.game_scene.menu_objects.create_server import CreateServer
from core.scene.game_scene import GameScene
from SnakeGame.game_scene.menu_objects.frame_rate import FrameRate
class MenuScene(GameScene):
    def __init__(self, name, screen):
        super().__init__(name, screen)
    def start(self):
        self.add_object(MenuPanel(self.canvas, name="main"), active=True)
        self.add_object(JoinServer(self.canvas, name="join_server"), active=False)
        self.add_object(CreateServer(self.canvas, name="create_server"), active=False)
        self.add_object(LoadingServer(self.canvas, name="loading_server"), active=False)
        self.add_object(FrameRate(self.canvas, name="frame_rate"), active=True)
        super().start() # すべてのオブジェクトのStartを実行
        