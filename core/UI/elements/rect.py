import pygame
from core.UI.ui_element import UIElement
from core.UI.rect_transform import RectTransform

class Rect(UIElement):
    """単色の矩形 (Rect) を描画する UI コンポーネント"""
    def __init__(self, canvas, base_size=None, rect_transform=None, color=pygame.Color(255, 255, 255, 255)):
        """
        :param canvas: UI を描画するキャンバス
        :param base_size: **キャンバス内の基準サイズ (`Vector2(width, height)`)**
        :param rect_transform: `RectTransform` インスタンス
        :param color: 矩形の色
        """
        if rect_transform is None:
            rect_transform = RectTransform(canvas, pygame.Vector2(0, 0), pygame.Vector2(1, 1))  # **デフォルトの位置とサイズ**
        super().__init__(canvas, rect_transform=rect_transform)

        self.base_size = canvas._parse_position(base_size) if base_size else pygame.Vector2(100, 50)  # **デフォルトサイズ**
        self.screen_size = pygame.Vector2(self.base_size)  # **スクリーンスケール**
        self.color = pygame.Color(color.r, color.g, color.b, color.a)  # **参照渡し防止**

        self.on_resize_screen()  # **初期スケール適用**

    def update_scale_rotation(self):
        """スケールと回転を適用"""
        # **現在の回転とスケールを取得**
        current_rotation = self.rect_transform.global_rotation  # **親の影響も考慮**
        scale = self.rect_transform.get_render_scale()
    
        # **スケール適用後のサイズを計算**
        final_width = max(1, int(self.base_size.x * scale.x))
        final_height = max(1, int(self.base_size.y * scale.y))

        # **回転後の矩形サイズを取得**
        angle = -current_rotation  # pygame の座標系は時計回り
        rotated_rect = pygame.Surface((final_width, final_height), pygame.SRCALPHA)
        rotated_rect.fill(self.color)
        self.transformed_surface = pygame.transform.rotate(rotated_rect, angle)

    def on_resize_screen(self):
        """ウィンドウサイズ変更時にスケールを更新"""
        scale = self.canvas.get_scale_factor()
        # **基準サイズを元にスケールを適用**
        new_width = int(self.base_size.x * scale.x)
        new_height = int(self.base_size.y * scale.y)

        # **サイズを更新**
        self.screen_size = pygame.Vector2(new_width, new_height)
        self.update_scale_rotation()

    def set_alpha(self, alpha):
        """透明度を変更"""
        self.color.a = alpha

    def render(self, screen):
        """回転・スケール適用後の矩形を描画"""
        if self.visible:
            pos = self.rect_transform.get_render_position()
            rect = self.transformed_surface.get_rect(center=(int(pos.x), int(pos.y)))
            screen.blit(self.transformed_surface, rect)

    def clone(self, new_rect_transform=None, new_color=None):
        """Rect クラスのコピーを作成"""
        return Rect(
            canvas=self.canvas,
            base_size=self.base_size,  # **同じ基準サイズ**
            rect_transform=new_rect_transform or self.rect_transform.clone(),  # **RectTransform をクローン**
            color=new_color if new_color is not None else self.color  # **色を変更可能**
        )
    def get_canvas_rect_size(self):
        """キャンバスのサイズを返す"""
        scale = self.rect_transform.get_render_scale()
        return pygame.Vector2(self.base_size.x * scale.x, self.base_size.y * scale.y)
