from core.network.network_component import NetworkComponent, sync
from core.network.network_manager import NetworkManager
import pygame

class NetworkTransform(NetworkComponent):
    """ネットワーク同期される Transform コンポーネント"""
    @sync
    def position_x(self): return self.game_object.transform.position.x

    @sync
    def position_y(self): return self.game_object.transform.position.y

    @sync
    def scale_x(self): return self.game_object.transform.scale.x

    @sync
    def scale_y(self): return self.game_object.transform.scale.y

    @sync
    def rotation_z(self): return self.game_object.transform.rotation.z

    def __init__(self, game_object, sync_interval=0.05):
        super().__init__(game_object, sync_interval)

    def on_sync_broadcast(self, diff):
        """Transform の同期データを送信"""
        diff["type"] = "transform_update"
        diff["network_id"] = self.network_id
        self.network_manager.broadcast(diff)
