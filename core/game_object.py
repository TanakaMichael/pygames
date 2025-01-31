from .coroutine import CoroutineManager
from .event_manager import EventManager

class GameObject:
    """ゲーム内のすべてのオブジェクトの基底クラス"""
    coroutine_manager = CoroutineManager()  # すべてのオブジェクト共通のコルーチン管理

    def __init__(self, name="GameObject"):
        self.name = name
        self.active = True
        self.components = {}  # **コンポーネントの辞書**
        self.event_manager = EventManager()

    def add_component(self, component_class, *args, **kwargs):
        """コンポーネントを追加 (引数を渡せるように修正)"""
        component = component_class(self, *args, **kwargs)  # **引数を渡してインスタンス化**
        component_name = component_class.__name__
        self.components[component_name] = component
        return component
    def has_component(self, component_name):
        """コンポー��ントが存在するか確認"""
        return component_name in self.components


    def get_component(self, component_type):
        """コンポーネントを取得"""
        return self.components.get(component_type.__name__)

    def remove_component(self, component_type):
        """コンポーネントを削除"""
        component_name = component_type.__name__
        if component_name in self.components:
            del self.components[component_name]

    def start_coroutine(self, func, *args):
        """コルーチンを開始"""
        return GameObject.coroutine_manager.start_coroutine(func, *args)

    def stop_coroutine(self, coroutine):
        """コルーチンを停止"""
        GameObject.coroutine_manager.stop_coroutine(coroutine)

    def update(self, delta_time):
        """毎フレーム更新処理 (delta_time を考慮)"""
        if self.active:
            for component in self.components.values():
                if hasattr(component, "update"):
                    component.update(delta_time)  # **各コンポーネントの update を呼び出す**
            GameObject.coroutine_manager.update(delta_time)

    def render(self, screen):
        """描画処理"""
        for component in self.components.values():
            if hasattr(component, "render"):
                component.render(screen)

    def register_event(self, event_name, callback):
        """ローカルイベントを登録"""
        self.event_manager.register_event(event_name, callback)

    def trigger_event(self, event_name, **kwargs):
        """ローカルイベントを発火"""
        self.event_manager.trigger_event(event_name, **kwargs)
