from core.component.component import Component
from .network_manager import NetworkManager
from core.network.network_component import NetworkComponent
from core.component.sprite import SpriteRenderer

class NetworkSprite(NetworkComponent):
    """スプライトのネットワーク同期コンポーネント"""
    def __init__(self, game_object, sync_interval=0.1):
        super().__init__(game_object, sync_interval=sync_interval, sync_name="sprite_update")
        self.sprite = self.game_object.get_component(SpriteRenderer)

        self.register_sync_variable(
            "image_path",
            lambda: self.sprite.image_path,
            lambda v: setattr(self.sprite, "image_path", v)
        )