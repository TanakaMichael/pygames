from core.component.sprite import SpriteRenderer
from core.component.collider import Collider
from core.component.rigidbody import RigidBody
from core.component.box_collider import BoxCollider
from core.component.circle_collider import CircleCollider
from core.camera import Camera
from core.canvas import Canvas
from core.network.network_game_object import NetworkGameObject
from core.network.network_object_factory import NetworkObjectFactory
from core.network.network_manager import NetworkManager
class GameScene:
    """ゲームシーンの基底クラス"""
    def __init__(self, name, screen):
        self.name = name
        self.objects = []  # シーン内のオブジェクトリスト
        self.camera = Camera()
        self.canvas = Canvas(screen)  # **各シーンに `Canvas` を持たせる**
        self.active = False  # 初期は非アクティブ
        self.network_manager = NetworkManager.get_instance()  # **NetworkManager の参照を保持**

    def start(self):
        """シーンがアクティブになったとき"""
        pass
    def end(self):
        """シーンが非アクティブになったとき"""
        pass

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
    def get_all_network_objects(self):
        """現在のシーン内の `NetworkGameObject` をすべて取得"""
        return [obj for obj in self.objects if isinstance(obj, NetworkGameObject)]

    def add_object(self, game_object):
        """シーンに GameObject を追加"""
        self.objects.append(game_object)
    def remove_object(self, game_object):
        """シーンから GameObject を削除"""
        if game_object in self.objects:
            self.objects.remove(game_object)
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
        self.camera.update(delta_time)
        self.canvas.update(delta_time)
        for obj in self.objects:

            if hasattr(obj, "update"):
                obj.update(delta_time)  # **obj が `update()` を持っている場合のみ呼び出す**
            else:
                print(f"⚠ update() を持たないオブジェクト: {obj}")

            if self.network_manager.is_server:
                self.handle_collisions()

    def handle_collisions(self):
        """サーバーのみ衝突判定を実行"""
        colliders = [obj.get_component(Collider) for obj in self.objects if obj.has_component(Collider)]

        for i in range(len(colliders)):
            for j in range(i + 1, len(colliders)):
                if colliders[i] is not None and colliders[i].check_collision(colliders[j]):
                    self.resolve_collision(colliders[i].game_object, colliders[j].game_object)
                    colliders[i].on_collision(colliders[j])

    def resolve_collision(self, obj1, obj2):
        """衝突時のレスポンス (速度の反射, 摩擦, 反発を適用)"""
        rb1 = obj1.get_component(RigidBody)
        rb2 = obj2.get_component(RigidBody)

        if not rb1 or not rb2:
            return

        # **どちらかが STATIC の場合、速度を反転**
        if rb1.collision_response == RigidBody.STATIC:
            rb2.velocity *= -rb2.physics_material.bounciness
        elif rb2.collision_response == RigidBody.STATIC:
            rb1.velocity *= -rb1.physics_material.bounciness
        else:
            # **動的な衝突 (反射)**
            normal = (obj2.transform.position - obj1.transform.position).normalize()
            v1 = rb1.velocity.dot(normal)
            v2 = rb2.velocity.dot(normal)

            rb1.velocity -= normal * v1 * (1 + rb1.physics_material.bounciness)
            rb2.velocity -= normal * v2 * (1 + rb2.physics_material.bounciness)

            # **摩擦の影響**
            rb1.velocity *= rb1.physics_material.friction
            rb2.velocity *= rb2.physics_material.friction

    def render(self, screen):
        """Layer の順にソートして描画"""
        self.canvas.render(screen)
        sorted_objects = sorted(self.objects, key=lambda obj: self.get_layer(obj))
        for obj in sorted_objects:
            obj.render(screen)

    def get_layer(self, obj):
        """オブジェクトの Layer を取得 (SpriteRenderer がある場合)"""
        sprite_renderer = obj.get_component(SpriteRenderer)
        return sprite_renderer.layer if sprite_renderer else 0
