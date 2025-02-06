from core.physics_engine import PhysicsEngine

class Floor:
    def __init__(self, name, level):
        self.name = name
        self.level = level                # 高さのレベル (例: 1階, 2階)
        self.objects = set()              # **オブジェクトをセットで管理 (重複防止)**
        self.transitional_objects = set() # **中間オブジェクトもセットで管理**
        self.scale_factor = 1.0           # デフォルトは 1.0 (通常サイズ)
        self.scene = None
        self.physics_engine = PhysicsEngine()

    # ✅ オブジェクト追加
    def add_object(self, game_object):
        if game_object not in self.objects:
            game_object._apply_floor(self.level)
            self.objects.add(game_object)
            game_object.set_scene(self.scene)

    # ✅ オブジェクト削除
    def remove_object(self, game_object):
        if game_object in self.objects:
            self.objects.remove(game_object)

    # ✅ 中間オブジェクト追加
    def add_transitional_object(self, game_object):
        if game_object not in self.transitional_objects:
            self.transitional_objects.add(game_object)

    # ✅ 中間オブジェクト削除
    def remove_transitional_object(self, game_object):
        if game_object in self.transitional_objects:
            self.transitional_objects.remove(game_object)

    # ✅ 更新処理
    def update(self, delta_time):
        # 物理エンジンの更新
        self.physics_engine.update_scene(list(self.objects | self.transitional_objects))
        self.physics_engine.update(delta_time)

        # オブジェクトの更新
        for obj in self.objects | self.transitional_objects:
            obj.update(delta_time)
    def handle_event(self, event):
        pass

    # ✅ 描画処理
    def render(self, camera, is_lower_floor=False):
        for obj in self.objects | self.transitional_objects:
            if obj.visible and obj.floor >= self.level:
               camera.register_object(obj, self.level)
    def start(self):
        for obj in self.objects | self.transitional_objects:
            if hasattr(obj, "start"):
                obj.start()
    def end(self):
        for obj in self.objects | self.transitional_objects:
            if hasattr(obj, "end"):
                obj.stop()