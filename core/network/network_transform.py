from core.network.network_component import NetworkComponent
from core.network.network_manager import NetworkManager
import pygame
class NetworkTransform(NetworkComponent):
    """ネットワーク同期される Transform コンポーネント"""
    def __init__(self, game_object, sync_interval=0.05):
        super().__init__(game_object, sync_interval)
        self.network_manager = NetworkManager.get_instance()
        # 例えば、game_object.transform は Transform オブジェクトとする
        self.register_sync_variable("position_x", self.game_object.transform.position, "x")
        self.register_sync_variable("position_y", self.game_object.transform.position, "y")
        self.register_sync_variable("scale_x", self.game_object.transform.scale, "x")
        self.register_sync_variable("scale_y", self.game_object.transform.scale, "y")
        self.register_sync_variable("rotation_x", self.game_object.transform.rotation, "x")
        self.register_sync_variable("rotation_y", self.game_object.transform.rotation, "y")
        self.register_sync_variable("rotation_z", self.game_object.transform.rotation, "z")

    def update(self, delta_time):
        """サーバーなら Transform をブロードキャスト"""
        super().update(delta_time)
    def on_sync_broadcast(self, diff): # 定期イベント
        """変数を同期します"""
        super().on_sync_broadcast(diff)
    def force_broadcast(self):
        """強制的に同期メッセージを送信するメソッド
        ※シーン更新完了時など、全ネットワークコンポーネントの最新状態をクライアントに送信する際に使用
        """
        self.on_sync_broadcast()
        self.prev_state = self._get_current_state()
    def handle_network_data(self, data):
        """受信データが Transform 更新かチェックして適用"""
        super().handle_network_data(data)
        
