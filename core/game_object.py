import pygame
from core.event_manager import EventManager
from core.coroutine import CoroutineManager
from core.component.transform import Transform
class GameObject:
    """親子関係を持つ GameObject クラス"""
    def __init__(self, name="GameObject", active=True, parent=None, scene=None):
        self.name = name
        self.components = {}  # **コンポーネントの辞書**
        self.event_manager = EventManager()  # **イベント管理**
        self.coroutine_manager = CoroutineManager()  # **コルーチン管理**
        self.children = []  # **子オブジェクトのリスト**
        self.scene = scene  # **所属するシーン**
        self.set_active(active)
        self.current_collisions = set()

        self.floor = 0

        # **デフォルトで Transform を追加**
        self.transform = self.add_component(Transform, parent=parent.transform if parent else None)

        # **親子関係をセット**
        self.parent = parent
    def _apply_floor(self, level):
        self.floor = level
    def set_floor(self, floor):
        if self.floor == floor:
            return  # 既に同じフロアなら何もしない

        # ✅ 現在のフロアから削除
        if isinstance(self.floor, (int, float)):
            if isinstance(self.floor, float):
                lower = int(self.floor)
                upper = lower + 1
                # 中間層から削除
                self.scene.world.get_floor(lower).remove_transitional_object(self)
                self.scene.world.get_floor(upper).remove_transitional_object(self)
            else:
                # 通常のフロアから削除
                self.scene.world.get_floor(self.floor).remove_object(self)

        # ✅ フロア更新
        self.floor = floor

        # 🚀 新しいフロアへ追加
        if isinstance(floor, float):
            # **中間層にいる場合、上下2つのフロアに追加**
            lower = int(floor)
            upper = lower + 1
            self.scene.world.get_floor(lower).add_transitional_object(self)
            self.scene.world.get_floor(upper).add_transitional_object(self)
        else:
            # **通常のフロアの場合は1つのフロアに追加**
            self.scene.world.get_floor(floor).add_object(self)

    def add_child(self, child_object):
        """子オブジェクトを追加"""
        if isinstance(child_object, GameObject):
            self.children.append(child_object)
            child_object.parent = self
            child_object.transform.set_parent(self.transform)
        else:
            raise ValueError("子オブジェクトは GameObject である必要があります")

    def add_component(self, component_class, *args, **kwargs):
        """コンポーネントを追加"""
        component = component_class(self, *args, **kwargs)
        self.components[component_class.__name__] = component
        return component

    def get_component(self, component_class):
        if component_class.__name__ in self.components:
            return self.components[component_class.__name__]

        # キャッシュされていない場合、基底クラスも含めて探索
        for comp in self.components.values():
            if isinstance(comp, component_class):
                return comp
        return None


    def on_collision_enter(self, other):
        print(f"🎯 プレイヤーが {other.name} と衝突しました！")

    def on_collision_exit(self, other):
        print(f"😌 {other.name} との衝突が終了しました。")
    def update(self, delta_time):
        """親の影響を考慮しつつ更新"""
        if not self.active:
            return

        # **自身の Transform を更新**
        self.transform.update_transform()

        # **コンポーネントの更新**
        for component in self.components.values():
            component.update(delta_time)

        # **コルーチンの更新**
        self.coroutine_manager.update(delta_time)

        # **子オブジェクトの更新**
        for child in self.children:
            child.update(delta_time)

    def handle_event(self, event):
        """イベント処理"""
        for component in self.components.values():
            component.handle_event(event)

        for child in self.children:
            child.handle_event(event)

    def set_scene(self, scene):
        """シーンを設定"""
        self.scene = scene
        for child in self.children:
            child.set_scene(scene)
    def set_active(self, active):
        """有効状態を設定"""
        self.active = active
        self.visible = active
        self.on_active()
        for child in self.children:
            child.set_active(active)
            child.on_active()

    def on_active(self):
        """有効化時のイベント"""
        pass

    def register_event(self, event_name, callback):
        """ローカルイベントを登録"""
        self.event_manager.register_event(event_name, callback)

    def trigger_event(self, event_name, **kwargs):
        """ローカルイベントを発火"""
        self.event_manager.trigger_event(event_name, **kwargs)
    def render(self, surface, screen_pos, scale):
        for component in self.components.values():
            component.render(surface, screen_pos, scale)
        for child in self.children:
            child.render(surface, screen_pos, scale)
