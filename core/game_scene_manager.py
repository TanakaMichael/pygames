from core.global_singleton import Global
class GameSceneManager(Global):
    """シーン管理と、シーン内のオブジェクト管理"""
    def __init__(self):
        if GameSceneManager._instance is not None:
            raise Exception("GameSceneManager はシングルトンです。`get_instance()` を使用してください")
        super().__init__()  # Global を初期化
        self.scenes = {}  # シーンリスト
        self.current_scene = None  # 現在のシーン

    def add_scene(self, scene):
        """シーンを登録"""
        self.scenes[scene.name] = scene

    def set_active_scene(self, name):
        """アクティブなシーンを切り替え"""
        if name in self.scenes:
            if self.current_scene:
                self.current_scene.active = False
            self.current_scene = self.scenes[name]
            self.current_scene.start()

    def update(self, delta_time):
        """アクティブシーンを更新"""
        if self.current_scene:
            self.current_scene.update(delta_time)

    def render(self, screen):
        """アクティブシーンを描画"""
        if self.current_scene:
            self.current_scene.render(screen)
    def get_current_scene(self):
        return self.current_scene
