# ファイル: core/component/network_component.py
from core.component.component import Component
from core.network.network_manager import NetworkManager

class NetworkComponent(Component):
    """ネットワーク同期可能なコンポーネントの基底クラス"""
    def __init__(self, game_object, sync_interval=0.05):
        super().__init__(game_object)
        self.network_manager = NetworkManager.get_instance()
        self.network_id = game_object.network_id  # オブジェクトの Network ID
        self.sync_interval = sync_interval          # 同期間隔 (秒)
        self.time_since_last_sync = 0               # 前回の同期経過時間
        self.prev_state = self._get_current_state()  # 前回送信した Transform 状態
    def update(self, delta_time):
        """サーバーなら、一定時間経過後に状態変化があれば同期メッセージを送信"""
        if self.network_manager.is_server:
            self.time_since_last_sync += delta_time
            if self.time_since_last_sync >= self.sync_interval:
                current_state = self._get_current_state()
                if current_state != self.prev_state:
                    self.on_sync_broadcast()
                    self.prev_state = current_state
                self.time_since_last_sync = 0
    def on_sync_broadcast(self):
        pass
    def handle_network_data(self, data):
        pass
    def _get_current_state(self):
        pass
    def force_broadcast(self):
        pass