from core.game_object import GameObject
from core.network.network_manager import NetworkManager

class NetworkGameObject(GameObject):
    """ネットワーク上で同期されるオブジェクト"""
    network_id_counter = 1  # **ID 管理**

    def __init__(self, name="NetworkGameObject", steam_id=-1):
        super().__init__(name)
        self.network_id = NetworkGameObject.network_id_counter
        self.steam_id = steam_id  # **所有者**
        NetworkGameObject.network_id_counter += 1
        self.is_networked = True
        self.is_local_player = False
        self.network_manager = NetworkManager.get_instance()
        self.network_manager.add_network_object(self)  # **登録**

        if self.network_manager.local_steam_id == steam_id:
            self.is_local_player = True

        # **サーバーなら全クライアントにスポーン通知**
        if self.network_manager.is_server:
            self.broadcast_spawn()

    def broadcast_spawn(self):
        """サーバーがクライアントにスポーン通知を送る"""
        spawn_data = {
            "type": "spawn",
            "network_id": self.network_id,
            "class_name": self.__class__.__name__,  # **クラス名を送る**
        }
        self.network_manager.broadcast(spawn_data)

    def receive_network_data(self, data):
        """すべてのネットワークコンポーネントにデータを渡す"""
        for component in self.components.values():
            if hasattr(component, "handle_network_data"):
                component.handle_network_data(data)
