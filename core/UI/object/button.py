import pygame
import math
from core.UI.ui_element import UIElement
from core.UI.elements.image import Image
from core.global_event_manager import GlobalEventManager
from core.UI.UIObject import UIObject
from core.input_manager import InputManager
from core.UI.rect_transform import RectTransform
class Button(UIObject):
    """クリック可能なボタン (3 つの `Image` を使用)"""
    def __init__(self, canvas, normal_path, hover_path, pressed_path, name="button",
                 base_size=pygame.Vector2(100, 50), position=pygame.Vector2(0, 0), rotation=0):
        """
        :param base_size: キャンパス内でのサイズを示す(スクリーンではない)"""
        super().__init__(canvas=canvas, rect_transform=RectTransform(canvas, position, local_rotation=rotation), name=name)
        self.base_size = base_size  # **キャンパス内でのサイズ**

        # **3 つの `Image` を作成**
        rect = RectTransform(canvas,local_position=pygame.Vector2(0, 0), local_rotation=rotation)
        self.normal_image = self.add_element(Image(canvas, normal_path, base_size=base_size, rect_transform=rect ))
        self.hover_image = self.add_element(Image(canvas, hover_path, base_size=base_size, rect_transform=rect))
        self.pressed_image = self.add_element(Image(canvas, pressed_path, base_size=base_size, rect_transform=rect))

        self.current_image = self.normal_image  # **最初は通常画像**
        self.is_hovered = False
        self.is_pressed = False

        self.global_event_manager = GlobalEventManager.get_instance()
        self.global_event_manager.register_event("resize_screen", self.on_resize_screen)

        self.input_manager = InputManager.get_instance()
        self.input_manager.register_event("MouseLeft", self.handle_press, "on_press")
        self.input_manager.register_event("MouseLeft", self.handle_hold, "on_hold")
        self.input_manager.register_event("MouseLeft", self.handle_release, "on_release")

    def get_position(self):
        """`Image` の現在の位置を取得"""
        return self.normal_image.get_position()

    def on_resize_screen(self):
        """ウィンドウサイズ変更時に `Image` のサイズを更新"""
        self.normal_image.on_resize_screen()
        self.hover_image.on_resize_screen()
        self.pressed_image.on_resize_screen()

    def update(self, delta_time):
        """ボタンの状態を更新 (回転を考慮)"""
        super().update(delta_time)

        # **スクリーン座標をキャンバス座標に変換**
        mouse_screen_pos = pygame.mouse.get_pos()
        mouse_canvas_pos = self.canvas.to_canvas_position(*mouse_screen_pos)
        canvas_to_screen_scale = self.canvas.get_scale_factor()

        # **ボタンの位置 & サイズを取得**
        pos = self.rect_transform.get_canvas_position()
        size = pygame.Vector2(self.base_size.x * canvas_to_screen_scale.x, self.base_size.y * canvas_to_screen_scale.y)

        # **回転角 (ラジアン) を取得**
        angle_rad = math.radians(self.rect_transform.local_rotation)

        # **マウス座標をボタンの中心基準で逆回転**
        dx = mouse_canvas_pos.x - pos.x
        dy = mouse_canvas_pos.y - pos.y
        rotated_x = (dx * math.cos(-angle_rad)) - (dy * math.sin(-angle_rad)) + pos.x
        rotated_y = (dx * math.sin(-angle_rad)) + (dy * math.cos(-angle_rad)) + pos.y

        # **マウスがボタンの範囲内にあるか判定 (回転後の座標を使用)**
        self.is_hovered = (
            pos.x - size.x / 2 <= rotated_x <= pos.x + size.x / 2 and
            pos.y - size.y / 2 <= rotated_y <= pos.y + size.y / 2
        )

        # **画像の切り替え**
        if self.is_pressed:
            self.set_active_image(self.pressed_image)
        elif self.is_hovered:
            self.set_active_image(self.hover_image)
        else:
            self.set_active_image(self.normal_image)



    def set_active_image(self, active_image):
        """現在の表示画像を変更"""
        if self.current_image != active_image:
            self.current_image.visible = False
            active_image.visible = True
            self.current_image = active_image

    def handle_press(self):
        """マウスが押された瞬間"""
        if self.is_hovered:
            self.is_pressed = True
            self.set_active_image(self.pressed_image)
            self.event_manager.trigger_event("on_pressed")

    def handle_hold(self):
        """マウスが押され続けている間"""
        if self.is_pressed and self.is_hovered:
            self.set_active_image(self.pressed_image)
            self.event_manager.trigger_event("on_hold")

    def handle_release(self):
        """マウスが離された瞬間"""
        if self.is_pressed and self.is_hovered:
            self.is_pressed = False
            self.event_manager.trigger_event("on_release")
        self.is_pressed = False

    def render(self, screen):
        """現在の画像を描画"""
        self.current_image.render(screen)
