from core.network.network_game_object import NetworkGameObject

class SnakeNetworkSync(NetworkGameObject):
    """スネークのネットワーク同期 (サーバーは全プレイヤーの動きを管理)"""
    def __init__(self, name="Snake"):
        super().__init__(name)

    def network_update(self):
        """スネークの同期 (サーバーが位置をブロードキャスト)"""
        if self.is_server:
            self.broadcast_position()
