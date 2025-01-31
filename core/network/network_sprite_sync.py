from core.component.component import Component
from .network_manager import NetworkManager
from core.component.sprite import SpriteRenderer

class NetworkSpriteSync(Component):
    """スプライトのネットワーク同期コンポーネント"""
    def __init__(self, game_object):
        super().__init__(game_object)
        self.network_manager = NetworkManager.instance

    def update(self, delta_time):
        """サーバーがスプライト情報を同期"""
        if self.network_manager.is_server:
            sprite_renderer = self.game_object.get_component(SpriteRenderer)
            if sprite_renderer:
                sync_data = {
                    "network_id": self.game_object.network_id,
                    "image_path": sprite_renderer.image_path,
                    "position": self.game_object.transform.position,
                    "scale": self.game_object.transform.scale,
                    "rotation": self.game_object.transform.rotation
                }
                self.network_manager.broadcast(sync_data)

    def handle_network_data(self, data):
        """受信データがスプライト更新かチェックして適用"""
        if data.get("type") == "sprite_update" and data.get("network_id") == self.game_object.network_id:
            sprite_renderer = self.game_object.get_component(SpriteRenderer)
            if sprite_renderer:
                sprite_renderer.image_path = data["image_path"]
