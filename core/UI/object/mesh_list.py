import pygame
import time
from core.UI.UIObject import UIObject
from core.UI.rect_transform import RectTransform
from core.UI.object.mesh_text_btn import ButtonText
from core.UI.elements.text import Text
from core.UI.elements.image import Image
from core.event_manager import EventManager
from core.input_manager import InputManager
from core.UI.elements.rect import Rect

class MeshList(UIObject):
    """クリック可能なリスト UI"""
    def __init__(self, canvas, name="UIList", position=pygame.Vector2(0, 0), rotation=0, 
                 item_data=None, item_size=pygame.Vector2(200, 50), spacing=None, 
                 max_visible_items=5, scroll_enabled=True, scroll_cooldown_time=0.1, 
                 on_item_click=None, font_path=None, font_ratio=0.05, font_color=(255, 255, 255), 
                 ui_background=pygame.Color(30, 30, 30, 255), alignment="center"
                 ):
        """
        :param item_data: **リストに表示するデータ (リスト型: str または Text インスタンス)**
        :param font_path: フォントのパス (デフォルト: None)
        :param font_ratio: フォントサイズ (キャンバス高さ比率)
        :param font_color: フォントの色
        :param scroll_cooldown_time: **スクロールのクールダウン時間 (秒)**
        """
        rect = RectTransform(canvas=canvas, local_position=position, local_rotation=rotation)
        super().__init__(canvas=canvas, name=name, rect_transform=rect.clone())

        self.item_data = item_data if item_data else []
        self.item_size = canvas._parse_position(item_size)
        self.spacing = spacing
        self.max_visible_items = max_visible_items
        self.scroll_enabled = scroll_enabled
        self.scroll_offset = 0  
        self.scroll_cooldown_time = scroll_cooldown_time  # **スクロールクールダウン時間**
        self.last_scroll_time = 0  # **最後にスクロールした時刻**


        self.alignment = alignment
        self.font_path = font_path
        self.font_ratio = font_ratio
        self.font_color = font_color
        self.on_item_click = on_item_click

        self.event_manager = EventManager()
        self.item_buttons = []
        self.init_ui(ui_background)
        self.create_list_items(self.item_data)
        self.rect_color = None

        # **スクロールイベント**
        self.input_manager = InputManager.get_instance()
        self.input_manager.register_event("ScrollUp", self.scroll_up, "on_scroll")
        self.input_manager.register_event("ScrollDown", self.scroll_down, "on_scroll")
    def init_ui(self, ui_background):
        rect = RectTransform(canvas=self.canvas, local_position=(0, ((self.item_size.y * self.max_visible_items) / 2) - self.item_size.y / 2))
        if isinstance(ui_background, pygame.Color):
            self.rect_color = pygame.Color(ui_background.r, ui_background.g, ui_background.b, ui_background.a)
            self.ui_background = self.add_element(Rect(self.canvas, base_size=(self.item_size.x, self.item_size.y * self.max_visible_items), color=self.rect_color, rect_transform=rect.clone()), -1)

        elif isinstance(ui_background, str): # おそらくpath
            self.ui_background = self.add_element(Image(self.canvas, ui_background, (self.item_size.x, self.item_size.y * self.max_visible_items)), -1)
    def end(self):
        """UI 要素を削除"""
        self.input_manager.unregister_event("ScrollUp", self.scroll_up, "on_scroll")
        self.input_manager.unregister_event("ScrollDown", self.scroll_down, "on_scroll")
        for btn in self.item_buttons:
            btn.end()
    def create_list_items(self, item_data):
        """リストの UI 要素を生成"""
        self.item_buttons.clear()
        self.clear_objects()

        for i, item in enumerate(item_data):
            # **Text インスタンスかチェック (str の場合は自動生成)**
            if isinstance(item, Text):
                text_instance = item.clone()
            else:
                text_instance = Text(
                    canvas=self.canvas,
                    value=item,
                    font_path=self.font_path,
                    font_ratio=self.font_ratio,
                    font_color=self.font_color
                )

            btn = ButtonText(
                canvas=self.canvas,
                name=f"ListItem_{i}",
                position=pygame.Vector2(0, 0),  # **初期位置はスクロールで調整**
                ui_text=text_instance, 
                fixed_background_size=self.item_size,
                alignment=self.alignment,
            )

            # **スペーシングの自動調整**
            if self.spacing is None:
                if i == 0:
                    btn_spacing = 0
                else:
                    prev_btn = self.item_buttons[-1]
                    btn_spacing = prev_btn.get_canvas_button_size().y / 2 + btn.get_canvas_button_size().y / 2
            else:
                btn_spacing = self.spacing

            # **ボタンの位置設定**
            btn.rect_transform.set_local_position(pygame.Vector2(0, btn_spacing * i))

            # **クリック時のイベント登録**
            if self.on_item_click:
                btn.event_manager.register_event("on_pressed", lambda idx=i: self.on_item_click(idx, item_data[idx]))

            self.item_buttons.append(btn)
            self.add_object(btn)

        self.update_item_positions()
    def get_canvas_size(self):
        return self.ui_background.get_canvas_rect_size()

    def update_item_positions(self):
        """現在の `scroll_offset` に基づいて UI アイテムの位置を更新"""
        start_index = self.scroll_offset
        end_index = min(len(self.item_buttons), start_index + self.max_visible_items)

        y_offset = 0  # **Y座標のオフセットをリセット**

        for i, btn in enumerate(self.item_buttons):
            if start_index <= i < end_index:
                btn.visible = True
                btn.rect_transform.set_local_position(pygame.Vector2(0, y_offset))
                y_offset += self.item_size.y + (self.spacing if self.spacing is not None else 0)
            else:
                btn.visible = False

    def update(self, delta_time):
        """リストの UI を更新"""
        super().update(delta_time)
        self.update_item_positions()

    def can_scroll(self):
        """スクロールできるか判定 (クールダウン考慮)"""
        current_time = time.time()
        if current_time - self.last_scroll_time >= self.scroll_cooldown_time:
            self.last_scroll_time = current_time
            return True
        return False

    def scroll_up(self, delta):
        """スクロールアップ"""
        if self.scroll_enabled and self.scroll_offset > 0 and self.can_scroll():
            self.scroll_offset = max(0, self.scroll_offset - int(delta))
            self.update_item_positions()

    def scroll_down(self, delta):
        """スクロールダウン"""
        if self.scroll_enabled and self.scroll_offset < len(self.item_buttons) - self.max_visible_items and self.can_scroll():
            self.scroll_offset = min(len(self.item_buttons) - self.max_visible_items, self.scroll_offset + int(abs(delta)))
            self.update_item_positions()

    def set_items(self, new_data):
        """リストのアイテムを更新"""
        self.item_data = new_data
        self.create_list_items(self.item_data)

    def render(self, screen):
        """リストの UI を描画"""
        super().render(screen)
