from core.global_singleton import Global
from core.network.network_object_factory import NetworkObjectFactory
from core.network.network_manager import NetworkManager
from core.network.network_game_object import NetworkGameObject
from core.network.network_game_scene import NetworkGameScene
import threading
class GameSceneManager(Global):
    """シーン管理と、シーン内のオブジェクト管理"""
    def __init__(self):
        if GameSceneManager._instance is not None:
            raise Exception("GameSceneManager はシングルトンです。`get_instance()` を使用してください")
        super().__init__()  # Global を初期化
        self.scenes = {}  # シーンリスト
        self.current_scene = None  # 現在のシーン
        self.network_manager = NetworkManager.get_instance()
        # シーン同期のリトライタイムアウト（秒）
        self.scene_sync_timeout = 10

    def add_scene(self, scene):
        """シーンを登録"""
        self.scenes[scene.name] = scene
    def get_current_scene_id(self):
        return self.current_scene.network_scene_id if self.current_scene else None

    def set_active_scene(self, name):
        """アクティブなシーンを切り替え"""
        if name in self.scenes:
            if self.current_scene:
                self.current_scene.set_active(False)
            self.current_scene = self.scenes[name]
            self.current_scene.set_active(True)
        else:
            print(f"gameScene: `{name}` が見つかりません")
    def set_active_server_scene(self, name):
        """サーバーでアクティブなシーンを切り替え"""
        self.set_active_scene(name)
        #self.network_manager.set_active_scene(name) # 自動client同期
    def set_active_scene_by_id(self, scene_id):
        """`NetworkGameSceneID` でシーンを切り替え"""
        for scene in self.scenes.values():
            if isinstance(scene, NetworkGameScene) and scene.network_scene_id == scene_id:
                self.set_active_scene(scene.name)
                return True
        print(f"⚠ シーン ID `{scene_id}` が見つかりません")
        return False

    def update(self, delta_time):
        """アクティブシーンを更新"""
        if self.current_scene:
            self.current_scene.update(delta_time)

    def render(self, screen):
        """アクティブシーンを描画"""
        if self.current_scene:
            self.current_scene.render(screen)
    def handle_event(self, event):
        """イベントを処理"""
        if self.current_scene:
            self.current_scene.handle_event(event)
    def get_current_scene(self):
        return self.current_scene
    def sync_scene_with_server(self):
        """クライアントがサーバーにシーン同期をリクエスト"""
        if self.network_manager.is_local_client:
            print("📡 シーン同期リクエストをサーバーに送信")
            self.network_manager.complete_scene_sync = False # シーンの更新が完了するまで False
            self.network_manager.send_to_server({
                "type": "request_scene_sync", 
                "sender_id": self.network_manager.local_steam_id
            })
            # タイマーをセットして、一定時間後に同期完了していなければ再リクエスト
            timer = threading.Timer(self.scene_sync_timeout, self.check_scene_sync_timeout)
            timer.start()
    def check_scene_sync_timeout(self):
        """
        シーン同期のリトライチェック

        一定時間たっても complete_scene_sync が False の場合、再度同期リクエストを送信する
        """
        if not self.network_manager.complete_scene_sync:
            print("⚠ シーン同期タイムアウト。再度シーン同期リクエストを送信します。")
            self.sync_scene_with_server()

    def handle_network_data(self, data):
        """ネットワークデータを受信し、適切な処理を実行"""
        if data.get("type") == "scene_sync":
            self.rebuild_scene(data["scene_data"], data["scene_id"])
        elif data.get("type") == "request_scene_sync" and self.network_manager.is_server:
            sender_id = data["sender_id"]
            print(f"📡 クライアント {sender_id} からシーン同期リクエスト")
            self.send_scene_sync(sender_id)
        elif data.get("type") == "force_broadcast_network_game_objects_components" and self.network_manager.is_server:
            self.force_broadcast_network_game_objects_components()
        elif data.get("type") == "scene_objects" and not self.network_manager.is_server:
            self.apply_scene_objects(data)
        elif data.get("type") == "request_scene_objects" and self.network_manager.is_server:
            sender_id = data["sender_id"]
            self.send_scene_objects(sender_id)
        if self.current_scene:
            self.current_scene.handle_network_data(data)

    def send_scene_sync(self, steam_id):
        """現在の `NetworkGameScene` の状態をクライアントに送信"""
        scene = self.current_scene
        scene_data = {
            "type": "scene_sync",
            "scene_id": scene.network_scene_id,
            "scene_data": {
                "objects": [
                    {
                        "class_name": obj.__class__.__name__,
                        "network_id": obj.network_id,
                        "steam_id": obj.steam_id
                    }
                    for obj in scene.get_all_network_objects()
                ]
            }
        }
        self.network_manager.send_to_client(steam_id, scene_data)
        print(f"📡 シーンデータを送信 {steam_id}")
    def send_broadcast_scene_sync(self):
        """シーンが更新された場合(サーバーがシーンを変えた)にclientに通知する"""
        for steam_id in self.network_manager.get_clients():
            self.send_scene_sync(steam_id)
    def send_scene_objects(self, target_id):
        """サーバーが新しいクライアントにシーンオブジェクトを送信"""
        scene = self.current_scene

        scene_data = {
            "type": "scene_objects",
            "scene_id": scene.network_scene_id,
            "objects": [
                {
                    "network_id": obj.network_id,
                    "class_name": obj.__class__.__name__,
                    "steam_id": obj.steam_id,
                }
                for obj in scene.get_all_network_objects()
            ]
        }
        self.network_manager.send_to_client(target_id, scene_data)

    def apply_scene_objects(self, data):
        """クライアントが受け取ったオブジェクトデータを適用"""
        if not self.set_active_scene_by_id(data["scene_id"]):
            return

        for obj_data in data["objects"]:
            new_obj = NetworkObjectFactory.create_object(
                obj_data["class_name"],
                obj_data["steam_id"],
                obj_data["network_id"]
            )
            if new_obj:
                self.current_scene.spawn_object(new_obj)

    def rebuild_scene(self, scene_data, scene_id):
        """サーバーから受け取ったデータでシーンを再構築"""
        print("🔄 シーンを再構築...")
        if not self.set_active_scene_by_id(scene_id):
            return
        # **NetworkGameObject のみを削除** (ローカルGameObjectは生成されているがNetworkObjectのNetIDが同期されていないため)
        self.current_scene.objects = [
            obj for obj in self.current_scene.objects if not isinstance(obj, NetworkGameObject)
        ]

        for obj_data in scene_data["objects"]:
            new_obj = NetworkObjectFactory.create_object(
                obj_data["class_name"],
                obj_data["steam_id"],
                obj_data["network_id"]
            )
            if new_obj:
                self.current_scene.spawn_object(new_obj)

        print("🔄 シーン再構築完了")
        self.network_manager.send_to_server({"type": "force_broadcast_network_game_objects_components"})
        self.network_manager.complete_scene_sync = True
    
    def force_broadcast_network_game_objects_components(self):
        """全クライアントに現在のオブジェクトのコンポーネントを再同期させる"""
        network_object = self.current_scene.get_all_network_objects()
        for obj in network_object:
            obj.force_broadcast_components()