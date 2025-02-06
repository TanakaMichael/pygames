import pygame
from core.panel import Panel
from core.UI.object.mesh_text import MeshText
from core.UI.object.mesh_text_btn import ButtonText
from core.UI.object.mesh_list import MeshList
from core.network.network_manager import NetworkManager
class JoinServer(Panel):
    def __init__(self, canvas=None, name="JoinServer", visible = True):
        FONT_PATH = "KH-Dot-Dougenzaka-12.ttf"
        super().__init__(name, canvas, visible)
        self.network_manager = NetworkManager.get_instance()
        self.join = self.add_ui(ButtonText(canvas, "return",font_path=FONT_PATH,ui_text="return",  font_ratio=0.05,position=("left+120", "top+80"), on_click=self.on_return))
        self.refresh = self.add_ui(ButtonText(canvas, name="refresh",font_path=FONT_PATH, ui_text="refresh", font_ratio=0.05,position=("center+300", "top+120"), on_click=self.on_refresh))
        # **リストのデータ (str + Text インスタンスの混在も可能)**
        list_items = [
            "アイテム1",
            "アイテム2",
            "アイテム4",
            "アイテム5",
            "アイテム6",
            "アイテム7"
        ]

        # **UIList を作成**
        self.ui_list = self.add_ui(MeshList(
            canvas=canvas,
            position=("center", "top+250"),
            item_data=list_items,
            item_size=(800, 100),
            max_visible_items=4,  
            scroll_enabled=True,  
            on_item_click=self.on_list_item_clicked,
            font_path=FONT_PATH,
            font_ratio=0.04,
            font_color=(255, 255, 255),
            alignment="left"
        ))
    def on_list_item_clicked(self, idx, item_data, **kwargs):
        print(f"Item Clicked: {idx}, {item_data}")
    def on_return(self):
        self.scene.get_object("main").set_active(True)
        self.scene.get_object("join_server").set_active(False)
    def on_refresh(self):
        print("Refreash")
        # 通信してサーバー情報更新
        lobbys = self.network_manager.get_friend_lobby()
        self.lobbys_data = []  # 現在のアイテムを削除
        for lobby in lobbys:
            lobby_id, friend =self.network_manager.get_lobby_data(lobby)
            num = self.network_manager.get_num_lobby_members(lobby)
            self.lobbys_data.append(f"{friend}:{lobby_id}, num_menbers={num}")
        self.ui_list.set_items(self.lobbys_data)



