import pygame
import json
import os
from core.global_singleton import Global
from core.network.network_manager import NetworkManager
from core.global_event_manager import GlobalEventManager

SPECIAL_KEYS = {
    "SPACE": "SPACE",
    "RETURN": "RETURN",
    "ENTER": "RETURN",
    "ESCAPE": "ESCAPE",
    "LEFT": "LEFT",
    "RIGHT": "RIGHT",
    "UP": "UP",
    "DOWN": "DOWN",
    "BUTTON_LEFT": "BUTTON_LEFT",
    "BUTTON_RIGHT": "BUTTON_RIGHT",
    "SCROLL_UP": "SCROLL_UP",
    "SCROLL_DOWN": "SCROLL_DOWN"
}

class InputManager(Global):
    """Unity風のイベント駆動型 InputManager (シングルトン)"""
    DEFAULT_BINDINGS = {
        "MoveUp": "w",
        "MoveDown": "s",
        "MoveLeft": "a",
        "MoveRight": "d",
        "MouseLeft": "BUTTON_LEFT",
        "MouseRight": "BUTTON_RIGHT",
        "ScrollUp": "SCROLL_UP",
        "ScrollDown": "SCROLL_DOWN"
    }

    def __init__(self, config_path="config.json"):
        if InputManager._instance is not None:
            raise Exception("InputManager is already initialized!")
        super().__init__()

        self.config_path = config_path
        self.key_bindings = self.load_bindings()
        self.event_listeners = {"on_press": {}, "on_hold": {}, "on_release": {}, "on_scroll": {}}
        self.server_event_listeners = {}
        self.network_manager = NetworkManager.get_instance()
        self.global_event_manager = GlobalEventManager.get_instance()
        self.held_keys = set()  # **押されているキーのセット**

        # **ユーザー退出イベントを監視**
        self.global_event_manager.register_event("on_player_leave", self._on_player_leave)

    def load_bindings(self):
        """キーバインドをロード (無ければデフォルト)"""
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                return json.load(f)
        return self.DEFAULT_BINDINGS.copy()

    def get_action_key(self, action):
        """アクション名から対応する pygame キーコードを取得"""
        key_name = self.key_bindings.get(action, "")

        if key_name.upper() in SPECIAL_KEYS:
            key_name = SPECIAL_KEYS[key_name.upper()]  # **特殊キーを大文字に変換**
            if key_name.startswith("BUTTON_"):
                return getattr(pygame, key_name, None)
        else:
            key_name = key_name.lower()  # **通常のキー（A-Z）は小文字に変換**

        return getattr(pygame, f"K_{key_name}", None) if key_name else None

    def register_event(self, action, callback, event_type="on_press"):
        """
        特定のアクションが発生した時のコールバックを登録
        :param action: "MoveUp" などのアクション名
        :param callback: 呼び出す関数
        :param event_type: "on_press", "on_hold", "on_release" のいずれか
        """
        if event_type not in self.event_listeners:
            raise ValueError("event_type は 'on_press', 'on_hold', 'on_release' のいずれか")

        if action not in self.event_listeners[event_type]:
            self.event_listeners[event_type][action] = []
        self.event_listeners[event_type][action].append(callback)
    def unregister_event(self, action, callback, event_type="on_press"):
        """
        イベントリスナーを解除
        :param action: 登録解除するアクション名 (例: "MoveUp")
        :param callback: 登録解除するコールバック関数
        :param event_type: イベントタイプ ("on_press", "on_hold", "on_release", "on_scroll")
        """
        if event_type in self.event_listeners and action in self.event_listeners[event_type]:
            if callback in self.event_listeners[event_type][action]:
                self.event_listeners[event_type][action].remove(callback)
                print(f"✅ イベント解除: {action} ({event_type})")
    
            # **コールバックがすべて解除された場合は、アクションを削除**
            if not self.event_listeners[event_type][action]:
                del self.event_listeners[event_type][action]

    def register_server_event(self, action, callback, valid_steam_id=None):
        """
        サーバーに対して入力イベントを登録
        - クライアントで入力が発生したらサーバーに送信
        - サーバーで受信したら `callback` を実行
        """
        if action not in self.server_event_listeners:
            self.server_event_listeners[action] = []
        self.server_event_listeners[action].append((callback, valid_steam_id))

    def trigger_event(self, action, event_type="on_press", **kwargs):
        """ローカルでイベントを発火"""
        if event_type in self.event_listeners and action in self.event_listeners[event_type]:
            for callback in self.event_listeners[event_type][action]:
                callback(**kwargs)

    def trigger_server_event(self, action, event_type="on_press", **kwargs):
        """クライアント側で入力イベントを検知し、サーバーに送信"""
        if not self.network_manager.connected:
            return
        if self.network_manager.is_local_client:
            data = {
                "type": "input",
                "event_type": event_type,
                "action": action,
                "sender_steam_id": self.network_manager.local_steam_id,
                **kwargs
            }
            self.network_manager.send_to_server(data)

        if self.network_manager.is_server:
            self.handle_network_data({
                "type": "input",
                "event_type": event_type,
                "action": action,
                "sender_steam_id": self.network_manager.server_id
            })

    def handle_event(self, event):
        """入力の監視 & イベント発火"""
        for action, key in self.key_bindings.items():
            mapped_key = self.get_action_key(action)

            if event.type == pygame.KEYDOWN and event.key == mapped_key:
                self.held_keys.add(action)
                self.trigger_event(action, "on_press")
                self.trigger_server_event(action, "on_press")

            elif event.type == pygame.KEYUP and event.key == mapped_key:
                self.held_keys.discard(action)
                self.trigger_event(action, "on_release")
                self.trigger_server_event(action, "on_release")
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == mapped_key:
                self.held_keys.add(action)
                self.trigger_event(action, "on_press")
                self.trigger_server_event(action, "on_press")
            elif event.type == pygame.MOUSEBUTTONUP and event.button == mapped_key:
                self.held_keys.discard(action)
                self.trigger_event(action, "on_release")
                self.trigger_server_event(action, "on_release")
            elif event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    self.trigger_event("ScrollUp", "on_scroll", delta=event.y)
                    self.trigger_server_event("ScrollUp", "on_scroll", delta=event.y)
                elif event.y < 0:
                    self.trigger_event("ScrollDown", "on_scroll", delta=event.y)
                    self.trigger_server_event("ScrollDown", "on_scroll", delta=event.y)

    def update(self, delta_time):
        """押しっぱなしのキーを処理"""
        for action in list(self.held_keys):
            self.trigger_event(action, "on_hold")
            self.trigger_server_event(action, "on_hold")

    def handle_network_data(self, data):
        """サーバーがクライアントからの入力を受信し、適切なオブジェクトのみ更新"""
        if data.get("type") == "input":
            action = data.get("action")
            event_type = data.get("event_type")
            sender_steam_id = data.get("sender_steam_id")

            if action in self.server_event_listeners:
                for callback, valid_steam_id in self.server_event_listeners[action]:
                    if valid_steam_id is None or sender_steam_id == valid_steam_id:
                        callback()

    def _on_player_leave(self, steam_id):
        """ユーザーが抜けた時に、その SteamID に紐づくすべてのイベントを削除"""
        for action in list(self.server_event_listeners.keys()):
            self.server_event_listeners[action] = [
                (callback, valid_steam_id)
                for callback, valid_steam_id in self.server_event_listeners[action]
                if valid_steam_id != steam_id
            ]
