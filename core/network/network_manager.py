import time
import ctypes
import json
import threading
import SteamNetworking as sn
from core.global_event_manager import GlobalEventManager
from core.coroutine import CoroutineManager, WaitForSeconds
from core.global_singleton import Global
import core.network.reconstruction as rc
class NetworkManager(Global):
    """サーバーとクライアントの管理 + 退出・シャットダウン機能追加"""
    def __init__(self):
        if NetworkManager._instance is not None:
            raise Exception("NetworkManager is not initialized!")
        super().__init__()
        self.network_objects = {}  # **ネットワーク同期するオブジェクト**
        self.server_id = None
        self.lobby_id = None
        self.running = True  # **メインループ制御**
        self.connected = False  # **接続状態**
        self.complete_scene_sync = False  # **シーン同期完了**
        self.global_event_manager = GlobalEventManager.get_instance()
        self.scene_manager = None
        # 欠損中のネットワークオブジェクトリクエスト用辞書
        # キー: network_id、値: {"last_request": タイムスタンプ, "attempts": 試行回数}
        self.missing_object_requests = {}
        # 再送信するまでのタイムアウト（秒）
        self.request_timeout = 5
        self.ping_rate = 0
        # EMA の係数。α の値は 0～1 の間で調整。1 に近いほど最新値を重視
        self.ema_alpha = 0.2
        self.last_ping_time = time.perf_counter()  # 高精度タイマーを利用

        # NetworkIDの初期化
        self.last_network_id = 0
    def generate_network_id(self):
        """ネットワークIDを生成"""
        self.last_network_id += 1
        return self.last_network_id
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
            print(f"✅ LobbyID: {self.lobby_id}に参加しました！")
        else:
            print("❌ 参加できるロビーがありません")
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
            # サーバー側は受信処理のみ（PINGのエコー応答を行う）
            threading.Thread(target=self.accept_p2p_sessions, daemon=True).start()
            threading.Thread(target=self.monitor_players, daemon=True).start()
        else:
            # クライアント側は定期的に PING_REQUEST を送信する
            threading.Thread(target=self.send_ping_request, daemon=True).start()

        threading.Thread(target=self.receive_messages, daemon=True).start()

        # 接続待機（クライアント側のみ）
        if self.is_local_client:
            threading.Thread(target=self.wait_for_ping, daemon=True).start()
    def send_ping_request(self):
        """クライアント側が定期的にサーバーへ PING_REQUEST を送信する"""
        while self.running and self.is_local_client:
            ping_request = {
                "type": "PING_REQUEST",
                "time": time.perf_counter(),
                "sender_id": self.local_steam_id
            }
            self.send_to_server(ping_request)
            time.sleep(1)
    def wait_for_ping(self):
        """サーバーから最初の PING_RESPONSE を受け取るまで待機"""
        print("⏳ サーバーからの PING_RESPONSE を待機中...")
        if self.is_server:
            return
        # 待機開始前に last_ping_time をリセット
        self.last_ping_time = time.perf_counter()
        while not self.connected:
            buffer = ctypes.create_string_buffer(2048)
            sender_steam_id = ctypes.c_uint64()

            if sn.receive_p2p_message(buffer, 2048, ctypes.byref(sender_steam_id)):
                try:
                    data = json.loads(buffer.value.decode('utf-8'))
                    # サーバーからのエコー応答(PING_RESPONSE)を確認
                    if data.get("type") == "PING_RESPONSE":
                        self.last_ping_time = time.perf_counter()
                        self.connected = True
                        self.running = True
                        print("✅ サーバーとの接続が確立しました！")

                        # サーバーにシーンオブジェクトのリクエストを送信し、欠損オブジェクトチェックも開始
                        if self.is_local_client:
                            self.request_scene()
                            threading.Thread(target=self.check_missing_requests, daemon=True).start()
                        break

                except json.JSONDecodeError:
                    continue

            if time.perf_counter() - self.last_ping_time > 20:
                print("❌ サーバーが応答しません。接続失敗!")
                exit()

        time.sleep(0.1)
    def check_missing_requests(self):
        """
        欠損オブジェクトリクエストの状態を定期的にチェックし、
        タイムアウトを超えている場合は再送信する。
        """
        while self.running:
            current_time = time.time()
            for network_id, req in list(self.missing_object_requests.items()):
                if current_time - req["last_request"] >= self.request_timeout:
                    req["last_request"] = current_time
                    req["attempts"] += 1
                    print(f"📡 （チェック）欠損オブジェクト (network_id: {network_id}) の再送要求（試行回数: {req['attempts']}）を送信中...")
                    self._send_missing_object_request(network_id)
            time.sleep(1)
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
    def get_clients_name(self):
        """現在のロビーにいるクライアントの名前リストを取得"""
        return [
            sn.get_steam_name(client_id)
            for client_id in self.get_clients()
        ]
    def send_ping(self):
        """サーバーがクライアントに PING を送信 (接続確認)"""
        while self.running and self.is_server:
            for player_id in self.get_clients():
                if player_id and player_id != self.server_id:
                    sn.send_p2p_message(player_id, json.dumps({"type": "PING", "time": time.perf_counter()}).encode())
            time.sleep(1)

    def accept_p2p_sessions(self):
        """新しい P2P セッションを受け入れ"""
        while self.running and self.is_server:
            for player_id in self.get_clients():
                if player_id and player_id != self.server_id:
                    sn.accept_p2p_session(player_id)
            time.sleep(1)

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

            self.scene_manager.current_scene.remove_object(obj.network_id)
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
    def process_ping(self, message):
        """
        クライアント側が PING_RESPONSE を受信した際の処理。
        送信時刻との差分から RTT を計算し、片道遅延（RTT/2）を EMA で平滑化する。
        """
        if message.get("type") != "PING_RESPONSE":
            return
        current_time = time.perf_counter()
        sent_time = message.get("time")
        if sent_time is not None:
            rtt = current_time - sent_time
            estimated_ping = rtt / 2.0
            if self.ping_rate == 0.0:
                self.ping_rate = estimated_ping
            else:
                self.ping_rate = self.ema_alpha * estimated_ping + (1 - self.ema_alpha) * self.ping_rate
            print(f"DEBUG: RTT = {rtt:.3f}, estimated ping = {estimated_ping:.3f}, smoothed ping_rate = {self.ping_rate:.3f}")
        self.last_ping_time = current_time

    def process_received_message(self, message):
        """
        再構築済みまたは断片化されていない受信メッセージを処理する。
        """
        msg_type = message.get("type")
        if msg_type == "PING_REQUEST":
            # サーバー側は PING_REQUEST を受信したらエコーして PING_RESPONSE を返す
            if self.is_server:
                response = {
                    "type": "PING_RESPONSE",
                    "time": message.get("time"),  # 送信側の時刻をそのまま返す
                    "sender_id": self.local_steam_id
                }
                self.send_to_client(message.get("sender_id"), response)
            return

        if msg_type == "PING_RESPONSE":
            # クライアント側が受信した PING_RESPONSE を処理する
            self.process_ping(message)
            return

        # シーン側の処理へ流す
        self.scene_manager.handle_network_data(message)

        # network_id が付属している場合は該当オブジェクトに転送
        network_id = message.get("network_id")
        if network_id is None:
            print("⚠ `network_id` が付属していないデータを無視")
            return
        scene = self.scene_manager.get_current_scene()
        if scene:
            obj = scene.get_object_by_network_id(network_id)
        if obj:
            obj.receive_network_data(message)
            if network_id in self.missing_object_requests:
                del self.missing_object_requests[network_id]
        else:
            if self.complete_scene_sync: # シーンの同期完了後にオブジェクトが存在しない場合は再送信の要請
                print(f"⚠ `network_id={network_id}` のオブジェクトが存在しません。欠損オブジェクトリクエストキューに登録します。")
                self.request_missing_object(network_id)
    def receive_messages(self):
        """受信データを断片化対応で処理する"""
        while self.running:
            buffer = ctypes.create_string_buffer(rc.FRAGMENT_BUFFER_SIZE)
            sender_steam_id = ctypes.c_uint64()

            if sn.receive_p2p_message(buffer, rc.FRAGMENT_BUFFER_SIZE, ctypes.byref(sender_steam_id)):
                try:
                    message = json.loads(buffer.value.decode('utf-8'))
                except json.JSONDecodeError:
                    continue

                # 断片の場合は再構築を試みる
                if message.get("type") == "fragment":
                    complete_message = rc.handle_incoming_fragment(message)
                    if complete_message:
                        self.process_received_message(complete_message)
                else:
                    self.process_received_message(message)

            time.sleep(0.05)
    def send_message(self, target_id, data):
        """
        送信するデータを JSON 化し、必要なら断片化して送信する。
        """
        message_bytes = json.dumps(data).encode('utf-8')
        if len(message_bytes) > rc.FRAGMENT_BUFFER_SIZE:
            rc.send_large_message(target_id, data, rc.FRAGMENT_BUFFER_SIZE)
        else:
            sn.send_p2p_message(target_id, message_bytes)
    def broadcast(self, data):
        """サーバーが全クライアントにデータを送信（断片化対応版）"""
        for player_id in self.get_clients():
            if player_id and player_id != self.server_id:
                self.send_message(player_id, data)

    def send_to_server(self, data):
        """クライアントがサーバーにデータを送信"""
        if self.is_local_client:
            self.send_message(self.server_id, data)
    def send_to_client(self, steam_id, data):
        """サーバーがクライアントにデータを送信（断片化対応版）"""
        if self.is_server:
            self.send_message(steam_id, data)
    def request_missing_object(self, network_id):
        """
        クライアントからサーバーへ、欠損しているネットワークオブジェクトの情報を要求する。
        既にリクエスト済みの場合は再送タイムアウトに基づき再送信を行う。
        """
        current_time = time.time()
        req = self.missing_object_requests.get(network_id)
        if req is None:
            # 初回リクエスト：登録して送信
            self.missing_object_requests[network_id] = {"last_request": current_time, "attempts": 1}
            self._send_missing_object_request(network_id)
        else:
            # 既にリクエスト済み。タイムアウトを超えていたら再送信
            if current_time - req["last_request"] >= self.request_timeout:
                req["last_request"] = current_time
                req["attempts"] += 1
                print(f"📡 欠損オブジェクト (network_id: {network_id}) の再送要求（試行回数: {req['attempts']}）を送信中...")
                self._send_missing_object_request(network_id)
    def _send_missing_object_request(self, network_id):
        request_data = {
            "type": "request_missing_object",
            "network_id": network_id,
            "sender_id": self.local_steam_id
        }
        self.send_to_server(request_data)

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
                # 重複チェック
                clients = self.get_clients()
                if steam_id in clients:
                    print(f"参加したユーザーはすでに存在します。: {steam_id}")
                    continue
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
