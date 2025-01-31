from core.game_scene_manager import GameSceneManager
from core.network.network_manager import NetworkManager
from core.global_event_manager import GlobalEventManager
from core.coroutine import CoroutineManager
from core.game import Game

class CoreInitializer:
    """ゲームのすべてのコアシステムを初期化"""
    
    def __init__(self, is_server=False):
        print("🔧 コアシステムの初期化を開始...")
        # game
        self.game = Game.get_instance()
        self.game.initialize(is_server)

        print("✅ コアシステムの初期化完了！")
    
    def get_scene_manager(self):
        return self.game.get_component(GameSceneManager)
    
    def get_network_manager(self):
        return self.game.get_component(NetworkManager)
    
    def get_event_manager(self):
        return self.game.get_component(GlobalEventManager)
    def update(self, dt):
        self.game.update(dt)
    def render(self, screen):
        self.game.render(screen)
