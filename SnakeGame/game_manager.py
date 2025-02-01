from core.game_object import GameObject
from core.global_event_manager import GlobalEventManager
from core.game_scene_manager import GameSceneManager
from core.network.network_game_object import NetworkGameObject
from core.game_scene_manager import GameSceneManager
from SnakeGame.snake import Snake
from core.network.network_manager import NetworkManager

class GameManager(GameObject):
    """ゲームの管理 (汎用)"""
    def __init__(self):
        super().__init__("GameManager")
        self.global_event_manager = GlobalEventManager.get_instance()
        self.network_manager = NetworkManager.get_instance()
        self.scene = GameSceneManager.get_instance().current_scene

        # **プレイヤーの参加・退出イベントをリスン**
        if self.network_manager.is_server:
            self.global_event_manager.register_event("on_player_join", self.on_player_join)
            self.global_event_manager.register_event("on_player_leave", self.on_player_leave)

    def on_player_join(self, steam_id):
        """プレイヤーが参加したときの処理"""
        print(f"🎮 プレイヤー {steam_id} が参加")
        print(f"現在サーバーにいるユーザーは: {self.network_manager.get_clients()}")

        # **新しいネットワークオブジェクトを作成**
        self.scene = GameSceneManager.get_instance().current_scene
        self.scene.spawn_object(Snake(name=f"Player_{steam_id}", steam_id=steam_id))

    def on_player_leave(self, steam_id):
        """プレイヤーが退出したときの処理"""
        print(f"🚪 プレイヤー {steam_id} が退出")
        self.scene = GameSceneManager.get_instance().current_scene
        # **対応するオブジェクトスを削除**ス
        objs = self.scene.get_objects_by_steam_id(steam_id)

        for obj in objs:
            print(f"obj: {objs}のオブジェクトを削除します")
            self.network_manager.remove_network_object(obj)
            self.scene.remove_object(obj)
