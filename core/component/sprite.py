import pygame
from core.component.component import Component
from core.component.transform import Transform
from core.game_scene_manager import GameSceneManager
import math
class SpriteRenderer(Component):
    """スプライトを描画するコンポーネント (2D)"""
    image_cache = {}  # 画像キャッシュ

    def __init__(self, game_object, image_path, layer=0):
        super().__init__(game_object)
        self.image_path = image_path
        self.last_image_path = None
        self.original_image = None
        self.transformed_image = None
        self.rect = None
        self.layer = layer

        self.rotation_x = 0  # X軸回転 (傾き)
        self.rotation_y = 0  # Y軸回転 (横回転)

        # **Transform を取得**
        self.transform = game_object.get_component(Transform)
        if not self.transform:
            raise ValueError("SpriteRenderer は Transform コンポーネントを必要とします")

        # **カメラを取得**
        self.camera = GameSceneManager.get_instance().get_current_scene().camera

        self.load_image()

    def load_image(self):
        """画像をロード (前回と異なる場合のみ)"""
        if self.image_path != self.last_image_path:
            if self.image_path in SpriteRenderer.image_cache:
                self.original_image = SpriteRenderer.image_cache[self.image_path]
            else:
                self.original_image = pygame.image.load(self.image_path).convert_alpha()
                SpriteRenderer.image_cache[self.image_path] = self.original_image
            self.last_image_path = self.image_path
            self.update_transform()

    def update_transform(self):
        """回転 & スケールを適用"""
        if self.original_image:
            # **回転 (rotation.z を 2D回転角とみなす)**
            angle = -self.transform.rotation.z  # 2Dゲームの場合 z成分を使用
            rotated = pygame.transform.rotate(self.original_image, angle)

            # **rect 設定 (center = transform.position)**
            self.transformed_image = rotated
            self.rect = self.transformed_image.get_rect()
            self.rect.center = (self.transform.position.x, self.transform.position.y)
    def apply_perspective_transform(self):
        """擬似的なX/Y軸回転を適用"""
        w, h = self.size
        x_shear = math.tan(math.radians(self.rotation_y)) * w * 0.5  # Y軸回転による横方向の歪み
        y_scale = math.cos(math.radians(self.rotation_x))  # X軸回転による縦の圧縮

        # Pygameでは直接Shearができないため、頂点変換を行う
        transformed_surf = pygame.transform.smoothscale(self.original_image, (w, int(h * y_scale)))
        return transformed_surf, x_shear

    def update(self, delta_time):
        """Transform の変更をチェック & 反映"""
        super().update(delta_time)
        self.load_image()
        self.update_transform()

    def render(self, screen):
        """カメラでワールド座標 → スクリーン座標に変換して描画 (スケール適用)"""
        super().render(screen)
        if not self.transformed_image:
            return
        # transformed_surf, x_shear = self.apply_perspective_transform()
        # new_rect = transformed_surf.get_rect(center=self.position)
        # **スクリーン座標に変換**
        screen_pos = self.camera.to_screen_position(self.transform.position)
        # **スケール (transform.scale) をカメラの screen_scale で適用**
        screen_scale = self.camera.to_screen_scale(self.transform.scale)
        final_width = int(self.transformed_image.get_width() * screen_scale.x)
        final_height = int(self.transformed_image.get_height() * screen_scale.y)

        # **最終的なスプライト**
        scaled_image = pygame.transform.scale(self.transformed_image, (final_width, final_height))
        screen.blit(scaled_image, screen_pos)
