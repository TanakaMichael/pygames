import pygame
from core.UI.rect_transform import RectTransform
from core.UI.component.UIComponent import UIComponent
from core.event_manager import EventManager
import copy
class UIElement:
    """すべての UI コンポーネントの基底クラス"""
    def __init__(self, canvas, name="ui", rect_transform=None,color=pygame.Color(255,255,255), layer=0, visible=True):
        self.ui_object = None
        self.canvas = canvas
        self.rect_transform = rect_transform
        self.color = color
        self.layer = layer
        self.visible = visible
        self.name = name
        self.event_manager = EventManager()  # **イベント管理システムを追加**
    def _set_object(self, ui_object):
        self.ui_object = ui_object

    def get_position(self):
        """Canvas のサイズに基づいて UI の描画位置を計算する"""
        return self.rect_transform.get_calculated_position()
    

    def update(self, delta_time):
        """更新処理（UIComponent も更新）"""
        self.rect_transform.update_transform()
    def render(self, screen):
        """描画処理"""
        if not self.visible:
            return
    def handle_event(self, event):
        pass
    def set_alpha(self, alpha):
        """画像の透明度を変更"""
        self.color.a = alpha
    def clone(self, new_name=None, new_rect_transform=None, **kwargs):
        """
        **UIElement のコピーを作成**
        
        :param new_name: 新しい名前（デフォルトは元の名前）
        :param new_rect_transform: 新しい RectTransform（デフォルトは元の座標をコピー）
        :param kwargs: サブクラス用の追加引数
        :return: 新しい UIElement のコピー
        """
        cloned_element = self.__class__(  # **現在のクラスを基に新しいインスタンスを作成**
            canvas=self.canvas,
            new_name=new_name or self.name,
            rect_transform=new_rect_transform or self.rect_transform.clone(),
            color=self.color,  # **色をコピー**
            layer=self.layer,
            visible=self.visible,
            **kwargs  # **追加引数を渡せるように**
        )

        # **イベントマネージャーのコピー**
        cloned_element.event_manager = copy.deepcopy(self.event_manager)

        return cloned_element