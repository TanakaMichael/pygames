from core.component.component import Component
from core.network.network_manager import NetworkManager
import pygame
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
            "type": "transform_update", 
            "network_id": self.network_id,
            "position_x": self.game_object.transform.position.x,
            "position_y": self.game_object.transform.position.y,
            "scale_x": self.game_object.transform.scale.x,
            "scale_y": self.game_object.transform.scale.y,
            "rotation_x": self.game_object.transform.rotation.x,
            "rotation_y": self.game_object.transform.rotation.y,
            "rotation_z": self.game_object.transform.rotation.z,
        }
        self.network_manager.broadcast(transform_data)
    def handle_network_data(self, data):
        """受信データが Transform 更新かチェックして適用"""
        if data.get("type") == "transform_update" and data.get("network_id") == self.network_id:
            self.game_object.transform.position = pygame.Vector2(data["position_x"], data["position_y"])
            self.game_object.transform.scale = pygame.Vector2(data["scale_x"], data["scale_y"])
            self.game_object.transform.rotation = pygame.Vector3(data["rotation_x"], data["rotation_y"], data["rotation_z"])
            print(f"📡 `network_id={self.network_id}` の Transform を更新")
