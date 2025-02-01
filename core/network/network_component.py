from core.component.component import Component
from core.network.network_manager import NetworkManager

def sync(func):
    """ネットワーク同期対象の変数をマークするデコレーター"""
    func._is_sync_variable = True  # フラグを設定
    return func

class NetworkComponent(Component):
    """ネットワーク同期可能なコンポーネントの基底クラス"""
    def __init__(self, game_object, sync_interval=0.05, sync_name="sync_update"):
        super().__init__(game_object)
        self.network_manager = NetworkManager.get_instance()
        self.network_id = game_object.network_id  # オブジェクトの Network ID
        self.sync_interval = sync_interval
        self.time_since_last_sync = 0
        self._sync_vars = {}  # 同期対象の変数辞書

        self.sync_name = sync_name

        # **@sync のついた変数を自動で登録**
        self._auto_register_sync_variables()

    def _auto_register_sync_variables(self):
        """@sync がついているメソッドをすべて同期対象として登録"""
        for attr_name in dir(self):
            attr = getattr(self.__class__, attr_name, None)
            if callable(attr) and hasattr(attr, "_is_sync_variable"):
                key = attr_name
                getter = lambda attr_name=attr_name: getattr(self, attr_name)()
                setter = lambda value, attr_name=attr_name: setattr(self, attr_name, lambda: value)
                self._sync_vars[key] = (getter, setter, getter())  # 初期値を取得

    def register_sync_variable(self, key, getter, setter):
        """同期対象の変数を手動で登録する"""
        self._sync_vars[key] = (getter, setter, getter())

    def update(self, delta_time):
        """サーバーなら、同期対象の変数をチェックし、変更があればブロードキャスト"""
        if self.network_manager.is_server:
            self.time_since_last_sync += delta_time
            if self.time_since_last_sync >= self.sync_interval:
                diff = {}
                for key, (getter, setter, last_val) in self._sync_vars.items():
                    current_val = getter()
                    if current_val != last_val:
                        diff[key] = current_val
                        self._sync_vars[key] = (getter, setter, current_val)  # 更新
                if diff:
                    self.on_sync_broadcast(diff)
                self.time_since_last_sync = 0

    def on_sync_broadcast(self, diff):
        """変更があったデータのみ送信"""
        data = {"type": self.sync_name, "network_id": self.network_id}
        data.update(diff)
        self.network_manager.broadcast(data)

    def force_broadcast(self):
        """強制的に全ての同期対象変数の値を送信"""
        diff = {key: getter() for key, (getter, setter, _) in self._sync_vars.items()}
        for key in diff:
            self._sync_vars[key] = (self._sync_vars[key][0], self._sync_vars[key][1], diff[key])
        self.on_sync_broadcast(diff)

    def handle_network_data(self, data):
        """受信データを適用"""
        if data.get("type") != self.sync_name or data.get("network_id") != self.network_id:
            return
        for key, value in data.items():
            if key in ("type", "network_id"):
                continue
            if key in self._sync_vars:
                getter, setter, _ = self._sync_vars[key]
                setter(value)
                self._sync_vars[key] = (getter, setter, value)  # 更新
