from core.network.network_component import NetworkComponent
from core.network.network_manager import NetworkManager
import pygame

class NetworkTransform(NetworkComponent):
    """ネットワーク同期される Transform コンポーネント"""

    def __init__(self, game_object, sync_interval=0.05):
        super().__init__(game_object, sync_interval, "transform_update")

        # **ネットワーク同期する変数を登録**
        self.register_sync_variable(
            "position_x",
            lambda: self.game_object.transform.position.x,
            lambda v: setattr(self.game_object.transform.position, "x", v)
        )
        self.register_sync_variable(
            "position_y",
            lambda: self.game_object.transform.position.y,
            lambda v: setattr(self.game_object.transform.position, "y", v)
        )
        self.register_sync_variable(
            "scale_x",
            lambda: self.game_object.transform.scale.x,
            lambda v: setattr(self.game_object.transform.scale, "x", v)
        )
        self.register_sync_variable(
            "scale_y",
            lambda: self.game_object.transform.scale.y,
            lambda v: setattr(self.game_object.transform.scale, "y", v)
        )
        self.register_sync_variable(
            "rotation_z",
            lambda: self.game_object.transform.rotation.z,
            lambda v: setattr(self.game_object.transform.rotation, "z", v)
        )
