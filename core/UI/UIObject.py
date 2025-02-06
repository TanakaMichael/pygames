import pygame
from core.UI.ui_element import UIElement
from core.UI.rect_transform import RectTransform
from core.event_manager import EventManager

class UIObject:
    """複数の UIElement を統括する親オブジェクト + 子オブジェクトを持てる"""
    def __init__(self, canvas, name="UIObject", rect_transform=None, visible=True, layer=0, parent=None):
        """
        :param canvas: 親 `Canvas`
        :param name: オブジェクト名
        :param rect_transform: 親 `RectTransform`（省略時はデフォルト）
        :param visible: 表示状態
        :param layer: レイヤー
        :param parent: 親オブジェクト
        """
        self.canvas = canvas
        self.name = name
        self.visible = visible
        self.active = visible
        self.rect_transform = rect_transform if rect_transform else RectTransform(canvas)
        self.rect_transform.parent = parent.rect_transform if parent else None  # **親の Transform を設定**
        self.elements = []  # **統括する UIElement リスト**
        self.components = {}  # **アタッチされたコンポーネント**
        self.children = []  # **子 UIObject**
        
        self.layer = layer
        self.color = pygame.Color(255, 255, 255, 255)  # **透過カラー**
        self.event_manager = EventManager()
    
    def set_alpha(self, alpha):
        """透明度を変更"""
        for element in self.elements:
            element.set_alpha(alpha)
        for child in self.children:
            child.set_alpha(alpha)
        self.color.a = alpha
    def get_canvas_size(self): 
        """最終的なUIの縦横を渡す"""
        pass
    def end(self):
        """オブジェクトの正常終了をおこなう(主にイベント)"""
        pass
    def add_element(self, ui_element, layer=0):
        """`UIElement` をこのオブジェクトに追加"""
        if isinstance(ui_element, UIElement):
            ui_element.layer = layer  # **レイ��ーを設定**
            self.elements.append(ui_element)
            ui_element.rect_transform.set_parent(self.rect_transform)
            ui_element._set_object(self)
            self.sort_render_list()
            return ui_element
        else:
            raise ValueError("追加するオブジェクトは UIElement である必要があります")

    def add_component(self, component_class, *args, **kwargs):
        """コンポーネントを追加 (アニメーション等)"""
        component = component_class(self, *args, **kwargs)  
        component_name = component_class.__name__
        self.components[component_name] = component
        return component
    def clear_objects(self):
        """オブジェクトをすべてクリア"""
        for child in self.children:
            if child in self.render_list:
                self.render_list.remove(child)
        self.children.clear()
    def remove_object(self, object):
        """オブジェクトを削除"""
        if object in self.children:
            self.children.remove(object)
        if object in self.render_list:
            self.render_list.remove(object)
    def get_component(self, component_name):
        """コンポー��ントを取得"""
        return self.components.get(component_name.__name__)

    def add_object(self, ui_object, layer=0):
        """子 UIObject を追加"""
        if isinstance(ui_object, UIObject):
            ui_object.layer = layer
            ui_object.rect_transform.set_parent(self.rect_transform) # **親の Transform を設定**
            self.children.append(ui_object)
            self.sort_render_list()
        elif isinstance(ui_object, UIElement):
            ui_object.rect_transform.set_parent(self.rect_transform)
            self.children.append(ui_object) # 本来はだめなのだが、描写順番で追加することがある。
    def set_active(self, visible):
        """オブジェクトの表示状態を設定"""
        self.visible = visible
        self.active = visible

    def update(self, delta_time):
        """全 UIElement、コンポーネント、および子 UIObject を更新"""
        if not self.active:
            return

        self.rect_transform.update_transform()  # **親オブジェクトの影響を更新**

        for component in self.components.values():
            if component.active:
                component.update(delta_time)


        for child in self.children:
            child.update(delta_time)  # **子オブジェクトも更新**
        for element in self.elements:
            element.update(delta_time)
    def handle_event(self, event):
        if not self.active:
            return
        for component in self.components.values():
            if component.active:
                component.handle_event(event)
            
        for element in self.elements:
            element.handle_event(event)
        
        for child in self.children:
            child.handle_event(event)
    def sort_render_list(self):
        """ソートが必要なときだけ `elements + children` を並べ替え"""
        self.render_list = sorted(self.elements + self.children, key=lambda obj: obj.layer)

    def render(self, screen):
        if self.visible:
            """事前ソート済みのリストを描画"""
            for component in self.components.values():
                if component.active:
                    component.render(screen)
            for obj in self.render_list:
                if obj.visible:
                    obj.render(screen)
