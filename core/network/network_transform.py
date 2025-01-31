from core.component.component import Component
from core.network.network_manager import NetworkManager

class NetworkTransform(Component):
    """ネットワーク同期される Transform コンポーネント"""
    def __init__(self, game_object, sync_interval=0.05):
        super().__init__(game_object)
        self.network_manager = NetworkManager.get_instance()
        self.network_id = game_object.network_id  # **オブジェクトの Network ID**
        self.sync_interval = sync_interval  # **同期間隔 (秒)**
        self.time_since_last_sync = 0  # **前回の同期時間**

    def update(self, delta_time):
        """サーバーなら Transform をブロードキャスト"""
        if self.network_manager.is_server:
            self.time_since_last_sync += delta_time
            if self.time_since_last_sync >= self.sync_interval:
                self.broadcast_transform()
                self.time_since_last_sync = 0

    def broadcast_transform(self):
        """サーバーが Transform をクライアントに送信"""
        transform_data = {
            "network_id": self.network_id,
            "position": self.game_object.transform.position,
            "rotation": self.game_object.transform.rotation
        }
        self.network_manager.broadcast(transform_data)
    def handle_network_data(self, data):
        """受信データが Transform 更新かチェックして適用"""
        if data.get("type") == "transform_update" and data.get("network_id") == self.network_id:
            self.game_object.transform.position = data["position"]
            self.game_object.transform.rotation = data["rotation"]
