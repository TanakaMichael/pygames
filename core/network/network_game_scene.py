from core.scene.game_scene import GameScene
from core.network.network_manager import NetworkManager
from core.network.network_object_factory import NetworkObjectFactory
from core.network.network_game_object import NetworkGameObject

class NetworkGameScene(GameScene):
    """ネットワーク対応の GameScene"""
    def __init__(self, name, screen):
        super().__init__(name, screen)
        self.network_manager = NetworkManager.get_instance()
        self.network_scene_id = self.network_manager.generate_scene_network_id()

    def start(self):
        """シーンがアクティブになったとき"""
        if self.network_manager.is_server:
            print(f"🌍 シーン `{self.name}` をサーバー側で開始")
        else:
            print(f"🎮 シーン `{self.name}` をクライアント側で開始")
    def update(self, dt):
        super().update(dt)
        
        

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
    def remove_object_by_network_id(self, network_id):
        """network_id を指定して `NetworkGameObject` のみ削除"""
        for obj in self.objects:
            if isinstance(obj, NetworkGameObject) and obj.network_id == network_id:
                self.remove_object(obj)
                print(f"🗑 `network_id={network_id}` の `NetworkGameObject` を GameScene から削除")
                return True
        print(f"⚠ `network_id={network_id}` の `NetworkGameObject` が見つかりません")
        return False

    def broadcast_spawn(self, game_object):
        """サーバーがクライアントにスポーン通知を送信"""
        spawn_data = {
            "type": "spawn_object",
            "network_id": game_object.network_id,
            "steam_id": game_object.steam_id,
            "class_name": game_object.__class__.__name__,
        }
        self.network_manager.broadcast(spawn_data)
    
    def send_missing_object(self, sender_id, network_id):
        """クライアントにオブジェクト再送要求を送信"""
        obj = self.get_object_by_network_id(network_id)
        spawn_data = {
            "type": "spawn_object",
            "network_id": obj.network_id,
            "steam_id": obj.steam_id,
            "class_name": obj.__class__.__name__,
        }
        if obj is not None:
            print(f"📡 クライアント {sender_id} に network_id {network_id} のオブジェクトを再送信")
            self.network_manager.send_to_client(sender_id, spawn_data)

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
        elif data.get("type") == "request_missing_object" and self.network_manager.is_server:
            network_id = data.get("network_id")
            sender_id = data.get("sender_id")
            print(f"📡 クライアント {sender_id} から network_id {network_id} の再送要求を受信しました")
            # 該当するオブジェクト情報を取得してクライアントへ送信する処理を実装
            self.send_missing_object(sender_id, network_id)

    def spawn_network_object(self, data):
        """クライアントがサーバーからのオブジェクト生成命令を受け取る"""
        network_id = data["network_id"]
        class_name = data["class_name"]
        steam_id = data["steam_id"]
        print(f"�� クライアントから network_id={network_id} の {class_name} を受信しました")

        new_object = NetworkObjectFactory.create_object(class_name,  steam_id ,network_id)
        if new_object:
            self.spawn_object(new_object)