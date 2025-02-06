import pygame
import math
from core.UI.ui_element import UIElement
from core.UI.elements.image import Image
from core.global_event_manager import GlobalEventManager
from core.UI.UIObject import UIObject
from core.input_manager import InputManager
from core.UI.rect_transform import RectTransform
from core.UI.object.mesh_text import MeshText
from core.UI.elements.text import Text
from core.UI.elements.rect import Rect
from core.UI.component.animation.move_animation import MoveAnimation

class ButtonText(UIObject):
    def __init__(self, canvas, name, position, ui_text, ui_image=pygame.Color(30,30,30,128), rotation=0, 
                 correction_background_scale=pygame.Vector2(1.2, 1.5), fixed_background_size=None, is_animation=None, 
                 on_click=None, font_path=None, font_ratio = 0.05, alignment="center"):
        """
        :param canvas: 親のキャンバス
        :param name: UIオブジェクトの名前
        :param position: ボタンの初期位置 (キャンバス座標)
        :param rotation: 回転角度
        :param ui_text: `Text` を継承した UI要素 (ボタンのラベル)
        :param ui_image: `Image` を継承した UI要素 (ボタンの背景) ※オプション
        """
        rect = RectTransform(canvas=canvas, local_position=position, local_rotation=rotation)
        super().__init__(canvas=canvas, name=name, rect_transform=rect)
        self.background_scale = correction_background_scale
        if fixed_background_size is not None:
            self.fixed_background_size = canvas._parse_position(fixed_background_size)
        else:
            self.fixed_background_size = None
        self.font_path = font_path
        self.font_ratio = font_ratio
        self.alignment = alignment  # **テキストの配置方式**
        self.init_ui_elements(canvas,ui_text, ui_image)

        self.animation = self.add_component(MoveAnimation)

        self.is_hovered = False
        self.is_pressed = False

        self.global_event_manager = GlobalEventManager.get_instance()
        self.global_event_manager.register_event("resize_screen", self.on_resize_screen)
        self.on_click = on_click

        self.input_manager = InputManager.get_instance()
        self.input_manager.register_event("MouseLeft", self.handle_press, "on_press")
        self.input_manager.register_event("MouseLeft", self.handle_hold, "on_hold")
        self.input_manager.register_event("MouseLeft", self.handle_release, "on_release")
    def init_ui_elements(self, canvas, ui_text, ui_image):
        self.rect_color = None  # Rect 背景用のカラー
        FONT_PATH = self.font_path

        # **ui_image の処理**
        if isinstance(ui_image, pygame.Color):
            self.rect_color = pygame.Color(ui_image.r, ui_image.g, ui_image.b, ui_image.a)  # **Rect 描画用のカラー**
            self.ui_image = self.add_element(Rect(canvas=canvas, color=self.rect_color), -1)
        else:
            ui_image.local_rect_transform = RectTransform(canvas=canvas, local_position=pygame.Vector2(0, 0))
            self.ui_image = self.add_element(ui_image, -1)
        # **ui_text が str の場合、自動で MeshText を作成**
        if isinstance(ui_text, str):
            rect = RectTransform(canvas)
            ui_text = Text(canvas, font_path=FONT_PATH, value=ui_text, rect_transform=rect, font_ratio=self.font_ratio)
        
        self.ui_text = self.add_element(ui_text)
        
    def end(self):
        """イベント登録解除"""
        self.global_event_manager.unregister_event("resize_screen", self.on_resize_screen)
        self.input_manager.unregister_event("MouseLeft", self.handle_press, "on_press")
        self.input_manager.unregister_event("MouseLeft", self.handle_hold, "on_hold")
        self.input_manager.unregister_event("MouseLeft", self.handle_release, "on_release")
    def on_resize_screen(self):
        """ウィンドウサイズ変更時に `Image` のサイズを更新"""
        if self.ui_image is not None:
            self.ui_image.on_resize_screen()
    def get_canvas_text_size(self):
        """キャンバス内のテキストのサイズを返す"""
        return self.ui_text.get_canvas_text_size()
    def get_canvas_button_size(self):
        """ボタンのキャンバス上の横幅を取得"""
        if self.fixed_background_size:
            return self.fixed_background_size  # **固定サイズがある場合はそのまま使用**

        # **Text のサイズを取得し、background_scale を適用**
        text_canvas_size = self.ui_text.get_canvas_text_size()
        width = text_canvas_size.x * self.background_scale.x
        height = text_canvas_size.y * self.background_scale.y
        return pygame.Vector2(width, height)
    def get_canvas_size(self):
        """キャンバス上に描写するときのサイズを返す"""
        return self.get_canvas_button_size()

    def update_background_size(self):
        """テキストのサイズに基づいて背景のサイズを更新"""
        if self.ui_image or self.rect_color:
            canvas_to_screen_scale = self.canvas.get_scale_factor()

            if self.fixed_background_size:
                # **固定背景サイズを使用**
                screen_size_x = self.fixed_background_size.x * canvas_to_screen_scale.x
                screen_size_y = self.fixed_background_size.y * canvas_to_screen_scale.y
            else:
                # **テキストサイズを基準に計算**
                text_canvas_size = self.ui_text.get_canvas_text_size()
                text_canvas_size.x *= self.background_scale.x
                text_canvas_size.y *= self.background_scale.y

                screen_size_x = text_canvas_size.x * canvas_to_screen_scale.x
                screen_size_y = text_canvas_size.y * canvas_to_screen_scale.y

            if self.ui_image:
                scale_factor_x = screen_size_x / self.ui_image.screen_size.x
                scale_factor_y = screen_size_y / self.ui_image.screen_size.y
                self.ui_image.rect_transform.set_local_scale(pygame.Vector2(scale_factor_x, scale_factor_y))
                self.ui_image.update_scale_rotation()
    def update_text_position(self):
        """テキストの配置を更新 (`left`, `center`, `right`)"""
        if not self.ui_text:
            return

        button_size = self.get_canvas_button_size()
        text_size = self.ui_text.get_canvas_text_size()

        if self.alignment == "left":
            x_offset = -button_size.x / 2 + text_size.x / 2  # 左端
        elif self.alignment == "right":
            x_offset = button_size.x / 2 - text_size.x / 2   # 右端
        else:
            x_offset = 0  # **中央 (デフォルト)**

        self.ui_text.rect_transform.set_local_position(pygame.Vector2(x_offset, 0))


    def update(self, delta_time):
        """ボタンの状態を更新"""
        super().update(delta_time)
        self.update_background_size()
        self.update_text_position()
        mouse_canvas_pos = self.canvas.to_canvas_position(*pygame.mouse.get_pos())

        # **背景サイズの取得**
        if self.fixed_background_size:
            text_canvas_size = self.fixed_background_size
        else:
            text_canvas_size = self.ui_text.get_canvas_text_size()
            text_canvas_size.x *= self.background_scale.x
            text_canvas_size.y *= self.background_scale.y

        pos = self.rect_transform.get_canvas_position()
        angle_rad = math.radians(self.rect_transform.get_render_rotation())

        dx = mouse_canvas_pos.x - pos.x
        dy = mouse_canvas_pos.y - pos.y
        rotated_x = (dx * math.cos(-angle_rad)) - (dy * math.sin(-angle_rad)) + pos.x
        rotated_y = (dx * math.sin(-angle_rad)) + (dy * math.cos(-angle_rad)) + pos.y

        self.is_hovered = (
            pos.x - text_canvas_size.x / 2 <= rotated_x <= pos.x + text_canvas_size.x / 2 and
            pos.y - text_canvas_size.y / 2 <= rotated_y <= pos.y + text_canvas_size.y / 2
        )


        # **画像の切り替え**
        if self.is_pressed:
            self.set_active_background(255)
            
        elif self.is_hovered:
            self.set_active_background(128)
        else:
            self.set_active_background(0)

    def handle_press(self):
        """マウスが押された瞬間"""
        if self.is_hovered and self.active:
            self.is_pressed = True
            #self.animation.start_to_delta_animation(pygame.Vector2(0, 20), 0.1)
            self.event_manager.trigger_event("on_pressed")

    def handle_hold(self):
        """マウスが押され続けている間"""
        if self.is_pressed and self.is_hovered and self.active:
            self.event_manager.trigger_event("on_hold")

    def handle_release(self):
        """マウスが離された瞬間"""
        if self.is_pressed and self.is_hovered and self.active:
            self.is_pressed = False
            #self.animation.return_to_delta_animation(0.2)
            self.event_manager.trigger_event("on_release")
            if self.on_click:  # **クリック判定**
                self.on_click()
        #else:
            #self.animation.return_to_delta_animation(0.1)
        self.is_pressed = False
    

    def set_active_background(self, value):
        """クリック時の背景 (暗くする)"""
        if self.ui_image:
            self.ui_image.set_alpha(value)  # **透明度変更**
        else:
            self.rect_color.a = value

    def render(self, screen):
        """ボタンの描画"""
        super().render(screen)


