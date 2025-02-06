from core.physics_engine import PhysicsEngine
from core.game_object import GameObject
class WorldLayer:
    def __init__(self, name, parallax_factor=1.0):
        self.name = name
        self.game_scene = None
        self.parallax_factor = parallax_factor
        self.objects = []
        self.transitional_objects = []
        self.physics_engine = PhysicsEngine()
        self.active = True

    def add_object(self, game_object, active=True):
        if isinstance(game_object, GameObject):
            game_object.layer = self
            self.objects.append(game_object)
            game_object.set_active(active)
            game_object.set_scene(self)
            return game_object
    def add_transitional_object(self, obj):
        """Layer 間の仮オブジェクトを追加"""
        self.transitional_objects.append(obj)

    def remove_object(self, obj):
        """オブジェクトを Layer から削除"""
        if obj in self.objects:
            self.objects.remove(obj)
        if obj in self.transitional_objects:
            self.transitional_objects.remove(obj)
        self.physics_engine.remove_object(obj)
    def render(self, screen, camera):
        """Layer の描画 (遠い Layer から描画)"""
        # 子のレイヤー内でのy座標ソート
        for obj in sorted(self.objects, key=lambda o: o.transform.global_position.y):
            obj.render(screen, camera)

        # 仮オブジェクトは適切な深度で描画
        for obj in self.transitional_objects:
            # このオブジェクトが現在のLayerよりも奥にある
            if self.should_render_in_current_layer(obj, camera):
                obj.render(screen, camera)
    def should_render_in_current_layer(self, obj, camera):
        """仮オブジェクトがこの Layer で描画されるべきか判定"""
        return obj.get_depth_factor() <= self.parallax_factor
    
    # ** 標準メソッド **
    def update(self, dt):
        if not self.active:
            return
        
        # 物理エンジンによる物理演算
        self.physics_engine.update_scene(self)
        self.physics_engine.update(dt)

        for obj in self.objects:
            obj.update(dt)