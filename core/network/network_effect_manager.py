from core.component import Component
from core.network.network_manager import NetworkManager
from core.game_object import GameObject
from core.component.sprite import SpriteRenderer
from core.component.animation_manager import AnimationManager
from core.coroutine import CoroutineManager

class NetworkEffectManager(Component):
    """サーバー主導でエフェクトを生成し、クライアントに通知"""
    def __init__(self, game_object):
        super().__init__(game_object)
        self.network_manager = NetworkManager.instance

    def create_effect(self, effect_name, position, duration=None):
        """エフェクトを生成し、クライアント全員に通知"""
        if self.network_manager.is_server:
            effect_data = {
                "type": "effect_create",
                "effect_name": effect_name,
                "position": position,
                "duration": duration
            }
            self.network_manager.broadcast(effect_data)

    def handle_network_data(self, data):
        """クライアントがエフェクトを受信してローカルで生成"""
        if data.get("type") == "effect_create":
            self.spawn_effect(data["effect_name"], data["position"], data["duration"])

    def spawn_effect(self, effect_name, position, duration):
        """エフェクト `GameObject` を作成 & `GameScene` に追加"""
        effect = GameObject(f"Effect_{effect_name}")
        effect.add_component(SpriteRenderer(effect, f"effects/{effect_name}.png", layer=10))

        # **アニメーションがある場合、継続時間を取得**
        animation_manager = AnimationManager(effect)
        animation_manager.add_animation(effect_name, self.get_effect_animation(effect_name))
        animation_manager.play_animation(effect_name)
        effect.add_component(animation_manager)

        # **持続時間を決定 (デフォルト: 1.0秒)**
        duration = duration or animation_manager.get_animation_duration(effect_name) or 1.0

        # **コルーチンで時間経過後にエフェクト削除**
        CoroutineManager.instance.start_coroutine(self.auto_destroy(effect, duration))

        # **GameScene に追加**
        self.game_object.scene.add_object(effect)

    def auto_destroy(self, effect, duration):
        """エフェクトの生存時間を管理し、削除"""
        yield duration
        self.game_object.scene.remove_object(effect)

    def get_effect_animation(self, effect_name):
        """エフェクトのアニメーションデータを取得 (仮)"""
        from core.component.animation import Animation
        import pygame
        sprite_sheet = pygame.image.load(f"effects/{effect_name}_spritesheet.png").convert_alpha()
        return Animation(sprite_sheet, frame_width=64, frame_height=64, frame_count=6, frame_duration=0.1)
