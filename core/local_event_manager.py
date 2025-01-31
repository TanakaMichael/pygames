from .event_manager import EventManager

class LocalEventManager(EventManager):
    """GameObject 内でのローカルイベント管理"""
    def __init__(self, owner):
        super().__init__()
        self.owner = owner  # 所属する GameObject
