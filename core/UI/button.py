import pygame
from .ui_element import UIElement
from core.input_manager import InputManager

class Button(UIElement):
    """クリック可能なボタン (InputManager によるイベントリ
    スン)"""
    def __init__(self, canvas, anchor=(0.5, 0.5), size=(120, 50), layer=1,
                 normal_sprite=None, hover_sprite=None, pressed_sprite=None,
                 on_click=None):
        super().__init__(canvas, anchor, size, "anchor", layer=layer)
        self.input_manager = InputManager.instance  # **シングルトンアクセス**
        
        # **ボタンのスプライト**
        self.normal_sprite = pygame.image.load(normal_sprite).convert_alpha() if normal_sprite else None
        self.hover_sprite = pygame.image.load(hover_sprite).convert_alpha() if hover_sprite else self.normal_sprite
        self.pressed_sprite = pygame.image.load(pressed_sprite).convert_alpha() if pressed_sprite else self.normal_sprite

        self.current_sprite = self.normal_sprite  # 初期状態は normal
        self.on_click = on_click  # **クリック時の処理**
        self.is_hovered = False
        self.is_pressed = False

        # **マウスクリック時のイベント登録**
        self.input_manager.register_event("MouseLeft", self.handle_click)

    def update(self, delta_time):
        """ボタンの状態を更新"""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        x, y = self.get_position()
        w, h = self.size

        # **マウスの位置チェック**
        self.is_hovered = (x <= mouse_x <= x + w) and (y <= mouse_y <= y + h)

        # **ボタンの状態を変更**
        if self.is_hovered:
            self.current_sprite = self.hover_sprite
        else:
            self.current_sprite = self.normal_sprite

    def handle_click(self):
        """ボタンがクリックされた時の処理 (InputManager から呼び出される)"""
        if self.is_hovered and self.on_click:
            self.current_sprite = self.pressed_sprite  # クリック時の画像変更
            self.on_click()  # **クリック処理を実行**

    def render(self, screen):
        """ボタンを描画"""
        if self.visible and self.current_sprite:
            position = self.get_position()
            screen.blit(self.current_sprite, position)
