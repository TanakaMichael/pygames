# ファイル: core/component/network_component.py
from core.component.component import Component
from core.network.network_manager import NetworkManager

class NetworkComponent(Component):
    """ネットワーク同期可能なコンポーネントの基底クラス
    ・同期対象の変数を「キー」と「対象オブジェクト＋属性名」のペアとして登録
    ・update() 時に各変数の現在値と前回値を比較し、変化があった場合のみ差分をブロードキャスト
    ・受信した差分データは自動的に対象の属性に書き込み
    """
    def __init__(self, game_object, sync_interval=0.05):
        super().__init__(game_object)
        self.network_manager = NetworkManager.get_instance()
        self.network_id = game_object.network_id  # オブジェクトの Network ID
        self.sync_interval = sync_interval          # 同期間隔 (秒)
        self.time_since_last_sync = 0               # 前回の同期経過時間
        # 同期対象変数の辞書： key -> (target_object, attribute_name, last_value)
        self._sync_vars = {}

    def register_sync_variable(self, key, target, attr_name):
        """同期対象の変数を登録する
        :param key: 同期時に使用するキー文字列
        :param target: 変数が存在する対象オブジェクト（例：game_object.transform）
        :param attr_name: 対象の属性名（例："x"）
        """
        initial_value = getattr(target, attr_name)
        self._sync_vars[key] = (target, attr_name, initial_value)

    def update(self, delta_time):
        """サーバー側なら、一定時間経過後に各同期対象変数の値をチェックし、変化があれば差分をブロードキャストする"""
        if self.network_manager.is_server:
            self.time_since_last_sync += delta_time
            if self.time_since_last_sync >= self.sync_interval:
                diff = {}
                for key, (target, attr, last_val) in self._sync_vars.items():
                    current_val = getattr(target, attr)
                    if current_val != last_val:
                        diff[key] = current_val
                        self._sync_vars[key] = (target, attr, current_val)
                if diff:
                    self.on_sync_broadcast(diff)
                self.time_since_last_sync = 0

    def on_sync_broadcast(self, diff):
        """差分データ diff をブロードキャストする
        デフォルトでは、"sync_update" タイプのメッセージとして送信
        """
        data = {"type": "sync_update", "network_id": self.network_id}
        data.update(diff)
        self.network_manager.broadcast(data)

    def force_broadcast(self):
        """強制的に全ての同期対象変数の値をブロードキャストする"""
        diff = {}
        for key, (target, attr, _) in self._sync_vars.items():
            current_val = getattr(target, attr)
            diff[key] = current_val
            self._sync_vars[key] = (target, attr, current_val)
        self.on_sync_broadcast(diff)

    def handle_network_data(self, data):
        """受信側で自動的に同期対象変数を更新する。
        送信側からの差分メッセージに含まれるキーと一致する変数に値を書き込みます。
        """
        if data.get("type") != "sync_update" or data.get("network_id") != self.network_id:
            return
        # data に含まれるキーのうち、"type" と "network_id" 以外を更新
        for key, value in data.items():
            if key in ("type", "network_id"):
                continue
            if key in self._sync_vars:
                target, attr, _ = self._sync_vars[key]
                setattr(target, attr, value)
                self._sync_vars[key] = (target, attr, value)
