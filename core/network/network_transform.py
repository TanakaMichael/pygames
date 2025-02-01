from core.network.network_component import NetworkComponent
from core.network.network_manager import NetworkManager
import pygame
class NetworkTransform(NetworkComponent):
    """ネットワーク同期される Transform コンポーネント"""
    def __init__(self, game_object, sync_interval=0.05):
        super().__init__(game_object, sync_interval)
        self.network_manager = NetworkManager.get_instance()

    def update(self, delta_time):
        """サーバーなら Transform をブロードキャスト"""
        super().update(delta_time)

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
    def _get_current_state(self):
        """現在の Transform の状態を辞書として取得"""
        return {
            "position_x": self.game_object.transform.position.x,
            "position_y": self.game_object.transform.position.y,
            "scale_x": self.game_object.transform.scale.x,
            "scale_y": self.game_object.transform.scale.y,
            "rotation_x": self.game_object.transform.rotation.x,
            "rotation_y": self.game_object.transform.rotation.y,
            "rotation_z": self.game_object.transform.rotation.z,
        }
    def on_sync_broadcast(self): # 定期イベント
        super().on_sync_broadcast()
        """サーバーが Transform 状態をクライアントに送信"""
        transform_data = {
            "type": "transform_update",
            "network_id": self.network_id,
            **self._get_current_state()
        }
        self.network_manager.broadcast(transform_data)
    def force_broadcast(self):
        """強制的に同期メッセージを送信するメソッド
        ※シーン更新完了時など、全ネットワークコンポーネントの最新状態をクライアントに送信する際に使用
        """
        self.on_sync_broadcast()
        self.prev_state = self._get_current_state()
    def handle_network_data(self, data):
        """受信データが Transform 更新かチェックして適用"""
        if data.get("type") == "transform_update" and data.get("network_id") == self.network_id:
            self.game_object.transform.position = pygame.Vector2(data["position_x"], data["position_y"])
            self.game_object.transform.scale = pygame.Vector2(data["scale_x"], data["scale_y"])
            self.game_object.transform.rotation = pygame.Vector3(data["rotation_x"], data["rotation_y"], data["rotation_z"])
