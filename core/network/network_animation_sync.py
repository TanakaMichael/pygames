from core.component.component import Component
from .network_manager import NetworkManager
from core.component.animation_manager import AnimationManager


class NetworkAnimationSync(Component):
    """アニメーションのネットワーク同期コンポーネント"""
    def __init__(self, game_object):
        super().__init__(game_object)
        self.network_manager = NetworkManager.instance
        self.last_sent_animation = None  # **直前に送信したアニメーション**

    def trigger_animation(self, animation_name):
        """アニメーションが変更されたときのみ送信"""
        if self.network_manager.is_server and animation_name != self.last_sent_animation:
            self.last_sent_animation = animation_name
            sync_data = {
                "network_id": self.game_object.network_id,
                "type": "animation_update",
                "animation": animation_name
            }
            self.network_manager.broadcast(sync_data)

    def handle_network_data(self, data):
        """クライアントがアニメーション変更を適用"""
        if data.get("type") == "animation_update" and data.get("network_id") == self.game_object.network_id:
            animation_manager = self.game_object.get_component(AnimationManager)
            if animation_manager:
                animation_manager.play_animation(data["animation"])
