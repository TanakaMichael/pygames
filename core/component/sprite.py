import pygame
import math
from core.component.component import Component
from core.component.transform import Transform

class Sprite(Component):
    """カメラによる描画を前提とした 2D スプライトコンポーネント"""
    image_cache = {}  # 画像キャッシュ

    def __init__(self, game_object, image_path, layer=0, base_size=None):
        """
        :param image_path: スプライト画像のパス
        :param layer: 描画レイヤー（数値が大きいほど手前に描画）
        :param base_size: 
            - None: 画像の元サイズを使用
            - (width, height): ピクセル指定
            - (ratio_x, ratio_y, "relative"): 画面比率で指定
        """
        super().__init__(game_object)
        self.image_path = image_path
        self.layer = layer
        self.base_size = pygame.Vector2(base_size)

        # Transform コンポーネント取得
        self.transform = game_object.get_component(Transform)
        if not self.transform:
            raise ValueError("Sprite には Transform コンポーネントが必要です")

        # 画像ロード
        self.original_image = None
        self.transformed_image = None
        self.load_image()

    def load_image(self):
        """画像のロードとキャッシュ"""
        if self.image_path not in Sprite.image_cache:
            Sprite.image_cache[self.image_path] = pygame.image.load(self.image_path).convert_alpha()

        self.original_image = Sprite.image_cache[self.image_path]
        self.apply_base_size()

    def apply_base_size(self):
        """基準サイズの適用（ズームや比率指定に対応）"""
        if self.base_size:
            if isinstance(self.base_size, tuple) and len(self.base_size) == 2:
                self.original_image = pygame.transform.scale(
                    self.original_image, (int(self.base_size[0]), int(self.base_size[1]))
                )

    def update(self, delta_time):
        """位置・回転・スケールの更新"""
        super().update(delta_time)
        self.update_transform()

    def update_transform(self):
        """Transform 情報を基にスプライトを変換"""
        scale = self.transform.get_render_scale()
        rotation = self.transform.get_render_rotation().z  # Z軸回転（2D）

        # スケーリング
        scaled_image = pygame.transform.scale(
            self.original_image,
            (int(self.original_image.get_width() * scale.x), int(self.original_image.get_height() * scale.y))
        )

        # 回転
        self.transformed_image = pygame.transform.rotate(scaled_image, -rotation)

    def render(self, surface, screen_position, scale):
        """カメラから呼び出されて描画を実行"""
        if not self.transformed_image:
            return

        rect = self.transformed_image.get_rect(center=(int(screen_position.x), int(screen_position.y)))
        surface.blit(self.transformed_image, rect)
