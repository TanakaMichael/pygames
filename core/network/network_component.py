from core.component.component import Component
from core.network.network_manager import NetworkManager

def sync(func):
    """ネットワーク同期対象の変数をマークするデコレーター"""
    func._is_sync_variable = True  # フラグを設定
    return func

class NetworkComponent(Component):
    """ネットワーク同期可能なコンポーネントの基底クラス
    ・@sync をつけた変数を自動的に同期対象として登録
    ・update() 時に変化があれば差分をブロードキャスト
    """

    def __init__(self, game_object, sync_interval=0.05):
        super().__init__(game_object)
        self.network_manager = NetworkManager.get_instance()
        self.network_id = game_object.network_id  # オブジェクトの Network ID
        self.sync_interval = sync_interval
        self.time_since_last_sync = 0

        # **同期対象変数の辞書 (key -> (getter, setter, last_value))**
        self._sync_vars = {}

        # **@sync をつけた変数を自動登録**
        self._auto_register_sync_variables()

    def _auto_register_sync_variables(self):
        """クラス内で @sync がついた変数を自動で登録する"""
        for attr_name in dir(self):
            attr = getattr(self.__class__, attr_name, None)
            if callable(attr) and hasattr(attr, "_is_sync_variable"):
                key = attr_name
                getter = lambda attr_name=attr_name: getattr(self, attr_name)()
                setter = lambda value, attr_name=attr_name: setattr(self, attr_name, lambda: value)
                self._sync_vars[key] = (getter, setter, getter())  # 初期値を取得

    def update(self, delta_time):
        """サーバーが同期変数の変更をチェックし、差分を送信"""
        if self.network_manager.is_server:
            self.time_since_last_sync += delta_time
            if self.time_since_last_sync >= self.sync_interval:
                diff = {}
                for key, (getter, setter, last_val) in self._sync_vars.items():
                    current_val = getter()
                    if current_val != last_val:
                        diff[key] = current_val
                        self._sync_vars[key] = (getter, setter, current_val)
                if diff:
                    self.on_sync_broadcast(diff)
                self.time_since_last_sync = 0

    def on_sync_broadcast(self, diff):
        """同期データをブロードキャスト"""
        data = {"type": "sync_update", "network_id": self.network_id}
        data.update(diff)
        self.network_manager.broadcast(data)

    def force_broadcast(self):
        """全ての同期変数を強制ブロードキャスト"""
        diff = {key: getter() for key, (getter, setter, _) in self._sync_vars.items()}
        for key in diff:
            self._sync_vars[key] = (self._sync_vars[key][0], self._sync_vars[key][1], diff[key])
        self.on_sync_broadcast(diff)

    def handle_network_data(self, data):
        """受信データを同期変数に適用"""
        if data.get("type") != "sync_update" or data.get("network_id") != self.network_id:
            return
        for key, value in data.items():
            if key in self._sync_vars:
                getter, setter, _ = self._sync_vars[key]
                setter(value)
                self._sync_vars[key] = (getter, setter, value)
