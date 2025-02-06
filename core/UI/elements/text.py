import pygame
import math
from core.UI.ui_element import UIElement
from core.global_event_manager import GlobalEventManager
from core.UI.rect_transform import RectTransform

class Text(UIElement):
    """テキスト UI コンポーネント (キャンバス比率 & ウィンドウサイズに応じてフォントサイズ調整 + 回転対応)"""
    def __init__(self, canvas, value="", font_path=None, font_ratio=0.05, font_color=(255, 255, 255), rect_transform=None):
        """
        :param canvas: テキストを描画するキャンバス
        :param value: 表示するテキスト
        :param font_path: フォントのパス
        :param font_ratio: **キャンバスの高さに対するフォントサイズ比率**
        :param font_color: フォントの色
        :param rect_transform: `RectTransform` (位置 & サイズ)
        """
        if rect_transform is None:
            rect_transform = RectTransform(canvas, pygame.Vector2(0, 0), pygame.Vector2(1, 1))  # **デフォルト位置とサイズ**
        super().__init__(canvas, rect_transform=rect_transform)
        self.value = value
        self.font_path = font_path
        self.font_ratio = font_ratio  # **フォントサイズを決める基準 (キャンバス高さの割合)**
        self.font_color = font_color
        self.font = None  # **フォントオブジェクト**
        self.rendered_text = None  # **レンダリング用テキスト**
        self.rotated_text = None  # **回転適用後のテキスト**

        self.global_event_manager = GlobalEventManager.get_instance()
        self.global_event_manager.register_event("resize_screen", self.on_resize_screen)

        self.update_font_size()
        self.set_text(value)

    def update_font_size(self):
        """キャンバスのサイズとウィンドウサイズに応じてフォントサイズを再計算"""
        canvas_height = self.canvas.get_canvas_size()[1]
        window_height = pygame.display.get_surface().get_height()

        # **キャンバスの高さに基づいて基本フォントサイズを計算**
        base_font_size = int(canvas_height * self.font_ratio)

        # **ウィンドウサイズの影響を加味 (スケール調整)**
        scale_factor = window_height / canvas_height
        final_font_size = max(10, int(base_font_size * scale_factor))  # **最低フォントサイズ 10 に制限**

        self.font = pygame.font.Font(self.font_path, final_font_size)

    def on_resize_screen(self):
        """ウィンドウサイズ変更時にフォントサイズを更新"""
        self.update_font_size()
        self.set_text(self.value)  # **リサイズ時に再レンダリング**


    def set_text(self, text):
        """テキストを設定 (スケールと回転を考慮)"""
        self.value = text
        self.rendered_text = self.font.render(self.value, True, self.font_color)

        # **現在のグローバル回転角度を取得**
        angle = -self.rect_transform.global_rotation  # **親の回転も考慮**

        # **回転適用**
        self.rotated_text = pygame.transform.rotate(self.rendered_text, angle)

        # **回転後のサイズを取得**
        rotated_width, rotated_height = self.rotated_text.get_size()

        # **回転後のオフセット補正 (中心位置を維持)**
        #offset_x = (rotated_width - self.rendered_text.get_width()) / 2
        #offset_y = (rotated_height - self.rendered_text.get_height()) / 2

        # **テキストのスクリーン座標を補正**
        #self.rect_transform.screen_position.x -= offset_x
        #self.rect_transform.screen_position.y -= offset_y
    def get_text_size(self):
        """描画するテキストの幅と高さを取得（より正確なサイズを使用）"""
        if self.font:
            # **pygame.font.Font.size() を使って正確なテキストのバウンディングボックスを取得**
            text_width, text_height = self.font.size(self.value)
            return pygame.Vector2(text_width, text_height)

        return pygame.Vector2(0, 0)  # **テキストが未設定の場合**
    def get_canvas_text_size(self):
        """キャンバスのサイズに基��きテキストの��と高さを計算"""
        canvas_size = self.canvas.get_canvas_size()  # **キャンバスサイズ**
        screen_size = pygame.display.get_surface().get_size()  # **スクリーンサイズ**
        text_screen_size = self.get_text_size()  # **テキストのスクリーンサイズ**
        
        # **スクリーン -> キャンバスのスケール比率**
        scale_x = canvas_size[0] / screen_size[0]
        scale_y = canvas_size[1] / screen_size[1]

        # **キャンバス内のテキストサイズを計算**
        return pygame.Vector2(
            text_screen_size.x * scale_x,
            text_screen_size.y * scale_y
        )


    def render(self, screen):
        """回転を考慮してテキストを描画"""
        if self.visible and self.rotated_text:
            pos = self.rect_transform.get_render_position()
            rotated_rect = self.rotated_text.get_rect(center=(int(pos.x), int(pos.y)))

            screen.blit(self.rotated_text, rotated_rect)

    def handle_event(self, event):
        """ウィンドウリサイズイベントをキャッチ"""
        if event.type == pygame.VIDEORESIZE:
            self.on_resize_screen()
    def clone(self, new_value=None, new_rect_transform=None):
        """Text クラスのコピーを作成（super().clone() を利用）"""
        return Text(
        canvas=self.canvas,
        value=new_value if new_value is not None else self.value,
        font_path=self.font_path,
        font_ratio=self.font_ratio,
        font_color=self.font_color,
        rect_transform=new_rect_transform or self.rect_transform.clone()
    )
