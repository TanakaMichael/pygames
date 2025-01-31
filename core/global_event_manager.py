from core.event_manager import EventManager
from core.global_singleton import Global

class GlobalEventManager(EventManager, Global):
    """シングルトンのグローバルイベントマネージャ"""
    def __init__(self):
        if GlobalEventManager._instance is not None:
            raise Exception("GameSceneManager はシングルトンです。`get_instance()` を使用してください")
        super().__init__()  # **Global を初期化**
