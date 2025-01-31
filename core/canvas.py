import pygame
class Canvas:
    """UI のルートコンテナ (ウィンドウサイズ基準)"""
    def __init__(self, screen):
        self.ui_elements = []
        self.screen = screen

    def add_element(self, element):
        """UI 要素を追加し、レイヤー順にソート"""
        self.ui_elements.append(element)
        self.ui_elements.sort(key=lambda e: e.layer)  # **レイヤー順にソート**

    def update(self, delta_time):
        """UI の更新処理"""
        for element in self.ui_elements:
            element.update(delta_time)

    def render(self, screen):
        """UI の描画処理 (レイヤー順)"""
        for element in self.ui_elements:
            if element.visible:
                element.render(screen)

    def get_canvas_size(self):
        """ウィンドウの現在のサイズを取得"""
        return pygame.display.get_window_size()
