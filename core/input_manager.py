import pygame
import json
import os
from core.global_singleton import Global
from core.network.network_manager import NetworkManager

class InputManager(Global):
    """Unity風のイベント駆動型 InputManager (シングルトン)"""
    DEFAULT_BINDINGS = {
        "MoveUp": "W",
        "MoveDown": "S",
        "MoveLeft": "A",
        "MoveRight": "D"
    }

    def __init__(self, config_path="config.json"):
        if InputManager._instance is None:
            InputManager.instance = self
        else:
            raise Exception("InputManager is already initialized!")
        super().__init__()

        self.config_path = config_path
        self.key_bindings = self.load_bindings()
        self.event_listeners = {}  # **ローカルイベント**
        self.server_event_listeners = {}  # **サーバーに送信するイベント**
        self.network_manager = NetworkManager.get_instance()

    def load_bindings(self):
        """キーバインドをロード (無ければデフォルト)"""
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                return json.load(f)
        return self.DEFAULT_BINDINGS.copy()

    def get_action_key(self, action):
        """アクション名から対応する pygame キーコードを取得"""
        key_name = self.key_bindings.get(action, "")
        return getattr(pygame, f"K_{key_name}", None)

    def register_event(self, action, callback):
        """特定のアクションが押された時のコールバックを登録"""
        if action not in self.event_listeners:
            self.event_listeners[action] = []
        self.event_listeners[action].append(callback)

    def register_server_event(self, action, callback, valid_steam_id=None):
        """
        サーバーに対して入力イベントを登録
        - クライアントで入力が発生したらサーバーに送信
        - サーバーで受信したら `callback` を実行
        """
        if action not in self.server_event_listeners:
            self.server_event_listeners[action] = []

        self.server_event_listeners[action].append((callback, valid_steam_id))

    def trigger_event(self, action):
        """ローカルでイベントを発火"""
        if action in self.event_listeners:
            for callback in self.event_listeners[action]:
                callback()

    def trigger_server_event(self, action):
        """クライアント側で入力イベントを検知し、サーバーに送信"""
        if self.network_manager.is_local_client:
            data = {
                "type": "input",
                "action": action,
                "sender_steam_id": self.network_manager.local_steam_id  # **送信者の Steam ID を含める**
            }
            self.network_manager.send_to_server(data)

    def update(self, dt):
        """入力の監視 & イベント発火"""
        for event in pygame.event.get():  # **ここで Pygame のイベントを取得**
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
    
            for action, key in self.key_bindings.items():
                mapped_key = self.get_action_key(action)
    
                if event.type == pygame.KEYDOWN and event.key == mapped_key:
                    self.trigger_event(action)  # **ローカルイベント発火**
                    self.trigger_server_event(action)  # **サーバーにも送信**

    def handle_network_data(self, data):
        """サーバーがクライアントからの入力を受信し、適切なオブジェクトのみ更新"""
        if data.get("type") == "input":
            action = data.get("action")
            sender_steam_id = data.get("sender_steam_id")  # **送信者の Steam ID**

            if action in self.server_event_listeners:
                for callback, valid_steam_id in self.server_event_listeners[action]:
                    # **送信者の Steam ID と有効な Steam ID が一致する場合のみ処理**
                    if valid_steam_id is None or sender_steam_id == valid_steam_id:
                        callback()
