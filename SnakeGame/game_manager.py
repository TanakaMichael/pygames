from core.game_object import GameObject
from core.global_event_manager import GlobalEventManager
from core.game_scene_manager import GameSceneManager
from core.network.network_game_object import NetworkGameObject
from SnakeGame.snake import Snake
from core.network.network_manager import NetworkManager

class GameManager(GameObject):
    """ゲームの管理 (汎用)"""
    def __init__(self):
        super().__init__("GameManager")
        self.global_event_manager = GlobalEventManager.get_instance()
        self.network_manager = NetworkManager.get_instance()

        # **プレイヤーの参加・退出イベントをリスン**
        if self.network_manager.is_server:
            self.global_event_manager.register_event("on_player_join", self.on_player_join)
            self.global_event_manager.register_event("on_player_leave", self.on_player_leave)

    def on_player_join(self, steam_id):
        """プレイヤーが参加したときの処理"""
        print(f"🎮 プレイヤー {steam_id} が参加")

        # **新しいネットワークオブジェクトを作成**
        self.scene = GameSceneManager.get_instance().current_scene
        self.scene.spawn_object(Snake(f"Player_{steam_id}", steam_id=steam_id))

    def on_player_leave(self, steam_id):
        """プレイヤーが退出したときの処理"""
        print(f"🚪 プレイヤー {steam_id} が退出")
        self.scene = GameSceneManager.get_instance().current_scene
        # **対応するオブジェクトを削除**
        obj = self.scene.get_object_by_steam_id(steam_id)
        if(obj is not None):
            self.network_manager.remove_object(obj)
