from core.game_scene import GameScene
from core.network.network_manager import NetworkManager
from core.network.network_object_factory import NetworkObjectFactory
from core.network.network_game_object import NetworkGameObject

class NetworkGameScene(GameScene):
    """ネットワーク対応の GameScene"""
    network_scene_id_counter = 1  # **全シーンで統一する ID**


    def __init__(self, name, screen):
        super().__init__(name, screen)
        self.network_manager = NetworkManager.get_instance()
        self.network_scene_id = NetworkGameScene.network_scene_id_counter
        NetworkGameScene.network_scene_id_counter += 1

    def start(self):
        """シーンがアクティブになったとき"""
        if self.network_manager.is_server:
            print(f"🌍 シーン `{self.name}` をサーバー側で開始")
        else:
            print(f"🎮 シーン `{self.name}` をクライアント側で開始")
        

    def get_all_network_objects(self):
        """現在のシーン内の `NetworkGameObject` をすべて取得"""
        return [obj for obj in self.objects if isinstance(obj, NetworkGameObject)]

    def spawn_object(self, game_object):
        """オブジェクトをシーンに追加し、必要なら全クライアントにスポーン指示を送る"""
        self.add_object(game_object)

        if isinstance(game_object, NetworkGameObject):
            if self.network_manager.is_server:
                self.broadcast_spawn(game_object)

    def remove_object(self, game_object):
        """オブジェクトを削除し、必要なら全クライアントに削除通知を送る"""
        if game_object in self.objects:
            self.objects.remove(game_object)

        if isinstance(game_object, NetworkGameObject):
            if self.network_manager.is_server:
                self.broadcast_remove(game_object.network_id)

    def broadcast_spawn(self, game_object):
        """サーバーがクライアントにスポーン通知を送信"""
        spawn_data = {
            "type": "spawn_object",
            "network_id": game_object.network_id,
            "steam_id": game_object.steam_id,
            "class_name": game_object.__class__.__name__,
        }
        self.network_manager.broadcast(spawn_data)

    def broadcast_remove(self, network_id):
        """サーバーがクライアントに削除通知を送信"""
        remove_data = {
            "type": "remove_object",
            "network_id": network_id
        }
        self.network_manager.broadcast(remove_data)

    def handle_network_data(self, data):
        """ネットワークデータを受信し、適切な処理を実行"""
        if data.get("type") == "spawn_object":
            self.spawn_network_object(data)
        elif data.get("type") == "remove_object":
            self.remove_object_by_network_id(data["network_id"])

    def spawn_network_object(self, data):
        """クライアントがサーバーからのオブジェクト生成命令を受け取る"""
        network_id = data["network_id"]
        class_name = data["class_name"]
        steam_id = data["steam_id"]

        new_object = NetworkObjectFactory.create_object(class_name,  steam_id ,network_id)
        if new_object:
            self.spawn_object(new_object)