from .component import Component
from .sprite import SpriteRenderer
from core.network.network_animation_sync import NetworkAnimationSync

class AnimationManager(Component):
    """アニメーションを管理し、ネットワーク同期を行う"""
    def __init__(self, game_object):
        super().__init__(game_object)
        self.animations = {}
        self.current_animation = None
        self.network_manager = game_object.network_manager
        self.network_sync = game_object.get_component(NetworkAnimationSync)  # **ネットワーク同期コンポーネント**
        self.sprite_renderer = game_object.get_component(SpriteRenderer)  # **スプライトを取得**
        if not self.sprite_renderer:
            raise ValueError("AnimationManager は SpriteRenderer を必要とします")

    def add_animation(self, name, animation):
        """アニメーションを登録"""
        self.animations[name] = animation

    def play_animation(self, name):
        """アニメーションを切り替える (ネットワーク同期)"""
        if name in self.animations and self.current_animation != name:
            self.current_animation = name
            if self.network_sync:
                self.network_sync.trigger_animation(name)

    def broadcast_animation_change(self, animation_name):
        """サーバーがクライアントにアニメーション変更を送信"""
        sync_data = {
            "network_id": self.game_object.network_id,
            "type": "animation_update",
            "animation": animation_name
        }
        self.network_manager.broadcast(sync_data)

    def handle_network_data(self, data):
        """クライアントがアニメーションデータを適用"""
        if data.get("type") == "animation_update" and data.get("network_id") == self.game_object.network_id:
            self.play_animation(data["animation"])

    def update(self, delta_time):
        """アクティブなアニメーションを更新"""
        super().update(delta_time)
        if self.current_animation:
            animation = self.animations[self.current_animation]
            animation.update(delta_time)
            self.sprite_renderer.image = animation.get_current_frame()  # **スプライトを更新**

    def get_current_frame(self):
        """現在のアニメーションフレームを取得"""
        if self.current_animation:
            return self.animations[self.current_animation].get_current_frame()
        return None
