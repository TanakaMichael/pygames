from core.game_object import GameObject
from core.panel import Panel
from core.UI.elements.text import Text
from core.UI.elements.image import Image
from core.UI.object.mesh_text import MeshText
from core.UI.object.mesh_image import MeshImage
from core.UI.object.button import Button
from core.network.network_manager import NetworkManager
from core.UI.component.animation.move_animation import MoveAnimation
from core.UI.component.animation.grid_reveal_animation import GridRevealAnimation
from core.UI.object.mesh_text_btn import ButtonText
from core.UI.object.button import Button
from core.UI.object.mesh_list import MeshList
import copy
import pygame
class MenuPanel(Panel):
    def __init__(self, canvas, name="PingUI", visible = True):
        FONT_PATH = "KH-Dot-Dougenzaka-12.ttf"
        super().__init__(name, canvas, visible)
        self.text = MeshText(canvas, "title",font_path=FONT_PATH,text="すねーくげーむう",  font_ratio=0.05,position=("center", "top-100"))
        self.text.add_component(MoveAnimation, target_position=("center", "top+100"))
        self.join_user = MeshText(canvas=canvas, name="users",font_path=FONT_PATH, position=("left+150", "bottom-25"), font_ratio=0.03)
        self.join_server_text = Text(canvas=canvas, value="join server", font_path=FONT_PATH)
        self.background = Image(canvas=canvas, image_path="SnakeGame/assets/Btn1.png")
        self.create_server = ButtonText(canvas=canvas, name="create_server", position=("center", "top-100"), ui_text=self.join_server_text.clone(new_value="create server"), ui_image=self.background.clone(), on_click=self.on_create_server)
        self.create_server.add_component(MoveAnimation, target_position=("center", "top+300"))
        self.join_server = ButtonText(canvas=canvas, name="join_server", position=("center", "top-100"), ui_text=self.join_server_text.clone(new_value="join server"), ui_image=self.background.clone(), on_click=self.on_join_server)
        self.join_server.add_component(MoveAnimation, target_position=("center", "top+400"))
        self.test_scene = ButtonText(canvas=canvas, name="test_scene", position=("right-100", "bottom-50"), ui_text=self.join_server_text.clone(new_value="TestScene"), ui_image=self.background.clone(), on_click=self.on_test_scene)
        self.test_scene.add_component(GridRevealAnimation, grid_size=(10, 10))
        self.add_ui(self.text)
        self.add_ui(self.join_user)
        self.add_ui(self.create_server)
        self.add_ui(self.join_server)
        self.add_ui(self.test_scene)
        self.network_manager = NetworkManager.get_instance()
        
    def on_join_server(self, **kwargs):
        print("join server clicked")
        self.scene.get_object("join_server").set_active(True)
        self.scene.get_object("main").set_active(False)
    def on_create_server(self, **kwargs):
        print("create server clicked")
        self.scene.get_object("create_server").set_active(True)
        self.scene.get_object("main").set_active(False)
    def on_test_scene(self, **kwargs):
        print("test scene clicked")
        from core.game_scene_manager import GameSceneManager
        gamesceneManager=GameSceneManager.get_instance()
        gamesceneManager.set_active_scene("TestScene") # ゲームの動作を確認するためのフィールド

    def update(self, dt):
        super().update(dt)
        self.join_user.set_text("Users: ")  # 初期化
        for user in self.network_manager.get_clients_name():
            self.join_user.add_text(f"{user}, ")
    def start(self):
        self.text.get_component(MoveAnimation).start()
        self.create_server.get_component(MoveAnimation).start()
        self.join_server.get_component(MoveAnimation).start()
        self.test_scene.get_component(GridRevealAnimation).start_fade_in()