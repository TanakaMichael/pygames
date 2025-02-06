from core.component.sprite import Sprite
from core.component.physics.collider import Collider
from core.component.physics.rigidbody import RigidBody
from core.component.transform import Transform
from core.game_object import GameObject
from core.camera import Camera
from core.canvas import Canvas
from core.network.network_game_object import NetworkGameObject
from core.network.network_manager import NetworkManager
from core.physics_engine import PhysicsEngine
from core.map.world_manager import WorldManager
# カメラがオブジェクトを描写する gameobject -> uiの順番で描写する
# sceneはすべてのLayerSceneを統括する
class GameScene:
    """ゲームシーンの基底クラス"""
    def __init__(self, name, screen, sorting_method="layer"):
        self.name = name
        self.world = WorldManager(self)
        self.canvas = Canvas(screen)  # **各シーンに `Canvas` を持たせる**
        self.active = False  # 初期は非アクティブ
        self.objects = []  # floorとは別のオブジェクト
        self.cameras = []  # 画面に表示するためのカメラ






    # ** オブジェクト **
    def add_object(self, game_object, active=True):
        if isinstance(game_object, GameObject):
            self.objects.append(game_object)
            game_object.set_active(active)
            game_object.set_scene(self)
            return game_object
    def remove_object(self, game_object):
        """シーンから GameObject を削除"""
        if game_object in self.objects:
            self.objects.remove(game_object)

    # ** カメラ **
    def add_camera(self, camera, active=True):
        """カメラをシーンに追加"""
        if isinstance(camera, Camera):
            self.cameras.append(camera)
            camera.set_active(active)
            camera.set_scene(self)
            return camera
    def remove_camera(self, camera):
        """カメラをシーンから削除"""
        if camera in self.cameras:
            self.cameras.remove(camera)

    # ** UI **
    def add_ui(self, ui):
        """UIObjectを追加します"""
        self.canvas.add_object(ui)
    def remove_ui(self, ui):
        """UI 要素を削除"""
        self.canvas.remove_object(ui)

    # ** setActive **
    def set_active(self, active):
        self.active = active
        if self.active:
            self.start()
        else:
            self.end()
    def start(self):
        """シーンがアクティブになったときの処理"""
        for obj in self.objects:
            if hasattr(obj, "start"):
                obj.start()
        self.world.start()
    def end(self):
        """シーンが非アクティブになったときの処理"""
        for obj in self.objects:
            if hasattr(obj, "end"):
                obj.end()
        self.world.end()
        self.reset()
    def reset(self):
        """ゲームシーンの完全リセット"""
        # すべてのオブジェクトとカメラを削除
        self.objects.clear()
        self.cameras.clear()

        # 物理エンジンのリセット
        self.physics_engine = PhysicsEngine()

        # UI のリセット
        self.canvas.clear()

        # シーン再起動
        self.start()  # **再度オブジェクトを追加する処理**


    def get_object(self, name):
        """指定した名前の GameObject を取得"""
        for obj in self.objects:
            if obj.name == name:
                return obj
        return None
    def get_object_by_steam_id(self, steam_id):
        """指定した network_id の GameObject を取得"""
        for obj in self.objects:
            if isinstance(obj, NetworkGameObject) and obj.steam_id == steam_id:
                return obj
        return
    
    def get_object_by_network_id(self, network_id):
        """network_id を指定して GameObject を取得"""
        for obj in self.objects:
            if isinstance(obj, NetworkGameObject) and obj.network_id == network_id:
                return obj
        return None
    def get_objects_by_steam_id(self, steam_id):
        """network_id を指定して GameObject のリストを返す"""
        return [obj for obj in self.objects if isinstance(obj, NetworkGameObject) and obj.steam_id == steam_id]
        
    def get_all_network_objects(self):
        """現在のシーン内の `NetworkGameObject` をすべて取得"""
        return [obj for obj in self.objects if isinstance(obj, NetworkGameObject)]
    def remove_object_by_network_id(self, network_id):
        """network_id を指定して `NetworkGameObject` のみ削除"""
        for obj in self.objects:
            if isinstance(obj, NetworkGameObject) and obj.network_id == network_id:
                self.remove_object(obj)
                print(f"🗑 `network_id={network_id}` の `NetworkGameObject` を GameScene から削除")
                return True
        print(f"⚠ `network_id={network_id}` の `NetworkGameObject` が見つかりません")
        return False
    
    def update(self, delta_time):
        """すべてのオブジェクトを更新 & 衝突判定"""
        if not self.active:
            return
        for obj in self.objects:
            if hasattr(obj, "update"):
                obj.update(delta_time)
        for camera in self.cameras:
            if hasattr(camera, "update"):
                camera.update(delta_time)
        self.world.update(delta_time)
        self.canvas.update(delta_time) # UIはcanvasがupdateをする
    def handle_event(self, event):
        """すべてのオブジェクトにイベントを処理"""
        if not self.active:
            return
        self.world.handle_event(event)
            
        self.canvas.handle_event(event)  # UIはcanvasが handle_eventをする
    def render(self, screen):
        """カメラとCanvasのRenderを処理"""
        if not self.active:
            return
        for camera in self.cameras:
            # 登録する
            self.world.render(camera)
            if hasattr(camera, "render_scene"):
                camera.render_scene(self.canvas.screen)  # **カメラが `render_scene()` を持っている場合のみ呼び出す**
        self.canvas.render(screen)  # UIはcanvasが renderをする
