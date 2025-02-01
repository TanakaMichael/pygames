# ファイル: core/ui/ui_element.py
import pygame
from core.UI.rect_transform import RectTransform

class UIElement:
    """すべての UI コンポーネントの基底クラス"""
    def __init__(self, canvas, name="ui", rect_transform=None, position_mode="anchor", color=pygame.Color(255,255,255), layer=0, visible=True):
        """
        :param canvas: この UI 要素を管理する Canvas
        :param rect_transform: RectTransform インスタンス（省略時はデフォルト値）
        :param position_mode: "anchor" または "absolute" で座標計算モードを選択
        :param color: UI 要素の背景色（例として矩形描画）
        :param layer: 描画レイヤー（数値が小さいほど下位レイヤー）
        :param visible: 表示フラグ
        """
        self.canvas = canvas
        self.rect_transform = rect_transform if rect_transform is not None else RectTransform()
        self.position_mode = position_mode
        self.color = color
        self.layer = layer
        self.visible = visible
        self.name = name

    def get_position(self):
        """Canvas のサイズに基づいて UI の描画位置を計算する"""
        canvas_size = self.canvas.get_canvas_size()
        return self.rect_transform.get_calculated_position(canvas_size, self.position_mode)

    def update(self, delta_time):
        """更新処理 (必要に応じてオーバーライド)"""
        pass

    def render(self, screen):
        """描画処理 (例として矩形を描画)"""
        if not self.visible:
            return
