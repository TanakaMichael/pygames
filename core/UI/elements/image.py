import pygame
from core.UI.ui_element import UIElement
from core.global_event_manager import GlobalEventManager
from core.UI.rect_transform import RectTransform

class Image(UIElement):
    """画像を描画する UI コンポーネント"""
    def __init__(self, canvas, image_path, base_size=None, rect_transform=None, color=pygame.Color(255,255,255,255)):
        """
        :param canvas: UI を描画するキャンバス
        :param image_path: 画像ファイルのパス
        :param base_size: **キャンバス内の基準サイズ (`Vector2(width, height)`)**
        :param rect_transform: `RectTransform` インスタンス
        :param color: 画像に適用するカラー
        """
        if rect_transform is None:
            rect_transform = RectTransform(canvas, pygame.Vector2(0, 0), pygame.Vector2(1, 1))  # **デフォルト位置とサイズ**
        super().__init__(canvas, rect_transform=rect_transform)
        self.image_path = image_path
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.base_size = base_size if base_size else pygame.Vector2(self.original_image.get_size())  # **基準サイズ**
        self.screen_size = pygame.Vector2(self.base_size) # **スクリーンスケール**

        self.canvas_image = self.original_image.copy()
        self.transformed_image = self.original_image
        self.color = pygame.Color(color.r, color.g, color.b, color.a)  # **参照渡し防止**
        

        # **初期スケール適用**
        self.apply_base_size()
        self.apply_color()  # **追加**
        self.on_resize_screen()

    def apply_base_size(self):
        """基準サイズ (`base_size`) に基づいて `original_image` をスケーリング"""
        self.original_image = pygame.transform.scale(self.original_image, (int(self.base_size.x), int(self.base_size.y)))

    def apply_color(self):
        """現在の `color` を適用"""
        if self.color:
            temp_image = self.original_image.copy()
            temp_image.fill(self.color, special_flags=pygame.BLEND_RGBA_MULT)
            self.original_image = temp_image
    def update_scale_rotation(self):
        """スケールと回転を適用"""
        # **現在の回転とスケールを取得**
        current_rotation = self.rect_transform.global_rotation  # **親の影響も考慮**
        scale = self.rect_transform.get_render_scale()
    
        # **スケール適用後のサイズを計算**
        final_width = max(1, int(self.original_image.get_width() * scale.x))
        final_height = max(1, int(self.original_image.get_height() * scale.y))
    
        # **スケールを適用 (original_image を基準にする)**
        scaled_image = pygame.transform.scale(self.original_image, (final_width, final_height))
    
        # **画像を回転**
        angle = -current_rotation  # pygame の座標系は時計回り
        rotated_image = pygame.transform.rotate(scaled_image, angle)
    
        # **回転後の画像サイズを取得**
        rotated_width, rotated_height = rotated_image.get_size()
    
        # **回転後の位置を補正 (中心を基準にする)**
        offset_x = (rotated_width - final_width) / 2
        offset_y = (rotated_height - final_height) / 2
    
        # **最終的な変換済み画像を保存**
        self.transformed_image = rotated_image
    
        # **最終的なスクリーン座標を調整**
        self.rect_transform.screen_position.x -= offset_x
        self.rect_transform.screen_position.y -= offset_y




    def on_resize_screen(self):
        """ウィンドウサイズ変更時にスケールを更新"""
        self.apply_color()  # **追加**
        scale = self.canvas.get_scale_factor()
        # **基準サイズを元にスケールを適用**
        new_width = int(self.base_size.x * (scale.x))
        new_height = int(self.base_size.y * (scale.y))

        # **画像をリスケール**
        self.original_image = pygame.transform.scale(self.canvas_image, (new_width, new_height))
        self.screen_size = pygame.Vector2(self.original_image.get_width(), self.original_image.get_height())
        self.update_scale_rotation()  # **スケールと回��を再計算**
    def handle_event(self, event):
        if event.type == pygame.VIDEORESIZE:
            self.on_resize_screen()
    def set_alpha(self, alpha):
        """画像の透明度を変更"""
        self.color.a = alpha
    

    def render(self, screen):
        """回転・スケール適用後の画像を描画"""
        if self.visible:
            pos = self.rect_transform.get_render_position()
            scale = self.rect_transform.get_render_scale()
            rect = self.transformed_image.get_rect(center=(int(pos.x), int(pos.y)))
            # **一時的なコピーを作成**
            temp_image = self.transformed_image.copy()
            temp_image.set_alpha(self.color.a)  # **個別に透過処理**
            screen.blit(temp_image, rect)
    def clone(self,new_rect_transform=None, new_color=None):
        """Image クラスのコピーを作成"""
        return Image(
            canvas=self.canvas,
            image_path=self.image_path,  # **同じ画像パスを使う**
            base_size=self.base_size,  # **同じ基準サイズ**
            rect_transform=new_rect_transform or self.rect_transform.clone(),  # **RectTransform をクローン**
            color=new_color if new_color is not None else self.color  # **色を変更可能**
        )

    def get_canvas_image_size(self):
        scale = self.rect_transform.get_render_scale()
        # **基準サイズを元にスケールを適用**
        return pygame.Vector2(int(self.base_size.x * (scale.x)), int(self.base_size.y * (scale.y)))