class Game:
    """ゲームのグローバルシングルトンマネージャー"""
    _instance = None

    @classmethod
    def get_instance(cls):
        """シングルトンインスタンスを取得"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if Game._instance is not None:
            raise Exception("Game はシングルトンです。`get_instance()` を使用してください")
        self.singletons = {}  # **シングルトンインスタンスを格納**
        self.initialize()

    def register_component(self, component):
        """シングルトンコンポーネントを登録"""
        self.singletons[component.__class__.__name__] = component

    def get_component(self, cls):
        """登録されたシングルトンコンポーネントを取得"""
        return self.singletons.get(cls.__name__)

    def initialize(self, is_server=False):
        """ゲーム開始時にシングルトンをセットアップ"""
        from core.game_scene_manager import GameSceneManager
        from core.network.network_manager import NetworkManager
        from core.global_event_manager import GlobalEventManager
        from core.input_manager import InputManager
        from core.game_scene_manager import GameSceneManager

        # **各シングルトンを登録**
        self.register_component(GameSceneManager.get_instance())
        self.register_component(NetworkManager.get_instance()) # スレッド動作
        self.register_component(GlobalEventManager.get_instance()) # 
        self.register_component(InputManager.get_instance())
        self.register_component(GameSceneManager.get_instance())  # 初期シーン登録

        # **ネットワークをセットアップ**
        # self.setup_network(is_server)

        print("✅ Game の初期化完了: すべてのシングルトンが登録されました")

    def setup_network(self, is_server=False):
        """ネットワークをセットアップ"""
        from core.network.network_manager import NetworkManager
        network_manager = self.get_component(NetworkManager)
        network_manager.initialize(is_server)

    def update(self, dt):
        """ゲーム全体の更新処理"""
        for singleton in self.singletons.values():
            if hasattr(singleton, "update"):
                singleton.update(dt)
    def render(self, screen):
        """ゲーム全体の描画処理"""
        for singleton in self.singletons.values():
            if hasattr(singleton, "render"):
                singleton.render(screen)
    def handle_event(self, event):
        """��ーム全体のイベント処理"""
        for singleton in self.singletons.values():
            if hasattr(singleton, "handle_event"):
                singleton.handle_event(event)
