from core.network.network_component import NetworkComponent
from core.component.physics.rigidbody import RigidBody
class NetworkRigidbody(NetworkComponent):
    """リジッドボディーのnetwork同期コンポネント"""
    def __init__(self, game_object, sync_interval=0.05):
        super().__init__(game_object, sync_interval, "rigidbody_update")
        self.rigidbody = self.game_object.get_component(RigidBody)
        # **リジッドボディーの同期する変数を登録**
        self.register_sync_variable(
            "velocity_x",
            lambda: self.rigidbody.velocity.x,
            lambda v: setattr(self.rigidbody.velocity, "x", v)  # 速度を更新する
        )
        self.register_sync_variable(
            "velocity_y",
            lambda: self.rigidbody.velocity.y,
            lambda v: setattr(self.rigidbody.velocity, "y", v)  # 速度を更新する
        )

        self.register_sync_variable(
            "acceleration_x",
            lambda: self.rigidbody.acceleration.x,
            lambda v: setattr(self.rigidbody.acceleration, "x", v)  # 加速度を更新する
        )
        self.register_sync_variable(
            "acceleration_y",
            lambda: self.rigidbody.acceleration.y,
            lambda v: setattr(self.rigidbody.acceleration, "y", v)  # 加速度を更新する
        )
        self.register_sync_variable(
            "collision_response",
            lambda: self.rigidbody.collision_response,
            lambda v: setattr(self.rigidbody, "collision_response", v)  # 衝突の種類を更新する
        )

        # クライアント予想が必要なものはNetworkRigidbodyをアタッチして、物理演算を更新する。

