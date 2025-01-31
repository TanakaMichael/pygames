import time
import ctypes
import json
import threading
import SteamNetworking as sn
from core.global_event_manager import GlobalEventManager
from core.coroutine import CoroutineManager, WaitForSeconds
from core.global_singleton import Global
class NetworkManager(Global):
    """サーバーとクライアントの管理 + 退出・シャットダウン機能追加"""
    def __init__(self):
        if NetworkManager._instance is not None:
            raise Exception("NetworkManager is not initialized!")
        super().__init__()
        self.network_id_map = {}  # **{ steam_id: network_id }**
        self.network_objects = {}  # **ネットワーク同期するオブジェクト**
        self.server_id = None
        self.lobby_id = None
        self.running = True  # **メインループ制御**
        self.connected = False  # **接続状態**
        self.last_ping_time = time.time()  # **最後に PING を受けた時間**
        self.global_event_manager = GlobalEventManager.get_instance()
        self.scene_manager = None
    def initialize(self, is_server=False):
        """サーバーの開始 or クライアントの参加"""
        self.is_server = is_server  # **サーバーかクライアントか**
        self.is_local_client = not is_server  # **ローカルクライアント**
        from core.game_scene_manager import GameSceneManager
        self.scene_manager = GameSceneManager.get_instance()

        if self.is_server:
            self.start_server()
        else:
            self.join_server()
    def start_server(self):
        """サーバーを開始 (ロビーを作成)"""
        if sn.initialize_steam():
            print("✅ Steam API 初期化成功")
        self.local_steam_id = sn.get_steam_id()
        print(f"🎮 自分の Steam ID: {self.local_steam_id}")
        self.lobby_id = sn.create_lobby(1, 4)  # 1: フレンドのみ
        sn.set_lobby_rich_presence(self.lobby_id)

        if self.lobby_id == 0:
            print("❌ ロビーの作成に失敗しました")
            exit()

        self.server_id = self.local_steam_id
        print(f"🏠 サーバー開始！ ロビー ID: {self.lobby_id}")

        # **スレッド起動**
        self.start_threads()

    def join_server(self):
        """クライアントとしてサーバーに接続"""
        if sn.initialize_steam():
            print("✅ Steam API 初期化成功")
        self.local_steam_id = sn.get_steam_id()
        print(f"🎮 自分の Steam ID: {self.local_steam_id}")

        lobbies = sn.get_friend_lobbies_richpresence()
        if len(lobbies) > 0:
            self.lobby_id = lobbies[0]
            sn.join_lobby(self.lobby_id)
            sn.set_lobby_rich_presence(self.lobby_id)
        else:
            print("❌ 参加できるロビーがありません")
            exit()

        if sn.join_lobby(self.lobby_id):
            print(f"✅ ロビーに参加しました！ ロビー ID: {self.lobby_id}")
        else:
            print("❌ ロビーへの参加に失敗しました")
            exit()

        self.server_id = sn.get_lobby_owner(self.lobby_id)
        print(f"🎮 サーバーの Steam ID: {self.server_id}")

        # **P2P セッション確立**
        sn.accept_p2p_session(self.server_id)

        # **スレッド起動**
        self.start_threads()

    def start_threads(self):
        """必要なスレッドを開始"""
        if self.is_server:
            threading.Thread(target=self.send_ping, daemon=True).start()
            threading.Thread(target=self.accept_p2p_sessions, daemon=True).start()
            threading.Thread(target=self.monitor_players, daemon=True).start()

        threading.Thread(target=self.receive_messages, daemon=True).start()
        # **接続が完了するまで待機**
        if self.is_local_client:
            threading.Thread(target=self.wait_for_ping, daemon=True).start()
    def wait_for_ping(self):
        """サーバーから最初の PING を受け取るまで待機"""
        print("⏳ サーバーからの PING を待機中...")
        if self.is_server:
            return
        while not self.connected:
            buffer = ctypes.create_string_buffer(512)
            sender_steam_id = ctypes.c_uint64()

            if sn.receive_p2p_message(buffer, 512, ctypes.byref(sender_steam_id)):
                try:
                    data = json.loads(buffer.value.decode())

                    if data["type"] == "PING":
                        self.last_ping_time = time.time()
                        self.connected = True
                        self.running = True
                        print("✅ サーバーとの接続が確立しました！")

                        # **サーバーに現在のシーンのオブジェクトをリクエスト**
                        if self.is_local_client:
                            self.request_scene()
                            break

                except json.JSONDecodeError:
                    continue

            if time.time() - self.last_ping_time > 20:
                print("❌ サーバーが応答しません。接続失敗!")
                exit()

            time.sleep(0.1)
    def request_scene(self):
        """クライアントがサーバーに現在のシーンをリクエスト"""
        print("📡 現在のシーンのオブジェクトをリクエスト中...")
        self.scene_manager.sync_scene_with_server()

    def get_clients(self):
        """現在のロビーにいるクライアントのリストを取得"""
        return [
            sn.get_lobby_member_by_index(self.lobby_id, i)
            for i in range(sn.get_num_lobby_members(self.lobby_id))
        ]

    def send_ping(self):
        """サーバーがクライアントに PING を送信 (接続確認)"""
        while self.running and self.is_server:
            for player_id in self.get_clients():
                if player_id and player_id != self.server_id:
                    sn.send_p2p_message(player_id, json.dumps({"type": "PING"}).encode())
            time.sleep(1)

    def accept_p2p_sessions(self):
        """新しい P2P セッションを受け入れ"""
        while self.running and self.is_server:
            for player_id in self.get_clients():
                if player_id and player_id != self.server_id:
                    sn.accept_p2p_session(player_id)
            time.sleep(0.1)

    def add_network_object(self, obj):
        """ネットワークオブジェクトを登録"""
        if obj.network_id not in self.network_objects:
            self.network_objects[obj.network_id] = obj
    def spawn_network_object(self, obj):
        """ネットワーク上にオブジェクトを生成する"""
        self.scene_manager.current_scene.add_object(obj)
        self.add_network_object(self, obj)
        # **生成リクエストをブロードキャスト**
        removal_data = {
            "network_id": obj,
            "type": "spawn_object"
        }
        if(self.is_server) :
            self.broadcast(removal_data)
    def remove_network_object(self, obj):
        """オブジェクトを削除し、全クライアントへ通知"""
        if obj.network_id in self.network_objects:
            del self.network_objects[obj.network_id]

            # **削除リクエストをブロードキャスト**
            removal_data = {
                "network_id": obj.network_id,
                "type": "remove_object"
            }
            if(self.is_server) :
                self.broadcast(removal_data)

            self.scene_manager.current_scene.remove_network_object(obj.network_id)
    def remove_network_object_by_network_id(self, network_id):
        """network_id を指定して `NetworkGameObject` のみ削除"""
        for obj in self.network_objects.values():
            if obj.network_id == network_id:
                self.remove_network_object(obj)
                return True
        return False
    def set_active_scene(self, scene_name):
        """アクティブなシーンを設定し、クライアントと同期"""
        if self.scene_manager.current_scene and self.scene_manager.current_scene.name == scene_name:
            print(f"🔄 シーン `{scene_name}` はすでにアクティブです")
            return

        # **シーン変更**
        self.scene_manager.set_active_scene(scene_name)
        self.current_scene_id = self.scene_manager.current_scene.network_id

        # **クライアントにシーン変更を通知 (サーバーのみ)**
        if self.is_server:
            self.broadcast_scene_change(scene_name)

    def broadcast_scene_change(self, scene_name):
        """シーン変更を全クライアントに送信"""
        scene_change_data = {
            "type": "scene_change",
            "scene_name": scene_name,
            "scene_id": self.current_scene_id
        }
        self.broadcast(scene_change_data)
    def apply_scene_change(self, data):
        """クライアントが受信したシーン変更を適用"""
        scene_name = data["scene_name"]
        scene_id = data["scene_id"]

        print(f"🌍 シーン `{scene_name}` に変更 (ID: {scene_id})")
        self.set_active_scene(scene_name)
    def receive_messages(self):
        """受信データを対応する `NetworkGameObject` に渡す"""
        while self.running:
            buffer = ctypes.create_string_buffer(512)
            sender_steam_id = ctypes.c_uint64()

            if sn.receive_p2p_message(buffer, 512, ctypes.byref(sender_steam_id)):
                try:
                    data = json.loads(buffer.value.decode())
                    # **PING は無視**
                    if data.get("type") == "PING":
                        continue
                    # シーンのhandle_network_dataを呼び出す
                    self.scene_manager.handle_network_data(data)

                    # `network_id` が付属しているかチェック
                    network_id = data.get("network_id")
                    if network_id is None:
                        print("⚠ `network_id` が付属していないデータを無視")
                        continue
                    

                    # 該当のオブジェクトにデータを渡す
                    obj = self.network_objects.get(network_id)
                    if obj:
                        obj.receive_network_data(data)
                    else:
                        print(f"⚠ `network_id={network_id}` のオブジェクトが存在しない")

                except json.JSONDecodeError:
                    print("❌ 受信データの JSON 解析に失敗")
                    continue

            time.sleep(0.05)
    def broadcast(self, data):
        """サーバーが全クライアントにデータを送信"""
        for player_id in self.get_clients():
            if player_id and player_id != self.server_id:
                sn.send_p2p_message(player_id, json.dumps(data).encode())

    def send_to_server(self, data):
        """クライアントがサーバーにデータを送信"""
        if self.is_local_client:
            sn.send_p2p_message(self.server_id, json.dumps(data).encode())

    def leave_lobby(self):
        """クライアントがロビーから退出"""
        if self.lobby_id:
            print(f"🚪 クライアントがロビー {self.lobby_id} から退出します")
            sn.leave_lobby(self.lobby_id)
            self.lobby_id = None
            self.running = False  # **スレッドを停止**
        else:
            print("⚠ 退出するロビーがありません")
    def monitor_players(self):
        """プレイヤーの参加・退出を監視 (サーバーのみ)"""
        while self.is_server:
            time.sleep(1)

            # **参加チェック**
            joined_steam_id = ctypes.c_uint64()
            joined_lobby_id = ctypes.c_uint64()
            if sn.check_lobby_join(ctypes.byref(joined_steam_id), ctypes.byref(joined_lobby_id)):
                steam_id = joined_steam_id.value
                self.global_event_manager.trigger_event("on_player_join", steam_id=steam_id)

            # **退出チェック**
            left_steam_id = ctypes.c_uint64()
            left_lobby_id = ctypes.c_uint64()
            if sn.check_lobby_leave(ctypes.byref(left_steam_id), ctypes.byref(left_lobby_id)):
                steam_id = left_steam_id.value
                self.global_event_manager.trigger_event("on_player_leave", steam_id=steam_id)

    def shutdown_server(self):
        """サーバーをシャットダウン"""
        print("🚨 サーバーをシャットダウンします")

        # **クライアント全員に通知**
        shutdown_message = json.dumps({"message": "SERVER_SHUTDOWN"})
        self.broadcast(shutdown_message)

        # **スレッド停止**
        self.running = False
        sn.shutdown_server()
        sn.leave_lobby(self.lobby_id)
        self.lobby_id = None

        print("✅ サーバーを正常にシャットダウンしました")
