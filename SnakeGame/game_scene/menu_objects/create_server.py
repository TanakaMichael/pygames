import pygame
from core.panel import Panel
from core.UI.object.mesh_text import MeshText
from core.UI.object.mesh_text_btn import ButtonText
from core.UI.object.mesh_list import MeshList
from core.network.network_manager import NetworkManager

class CreateServer(Panel):
    def __init__(self, canvas, name="CreateServer", visible=False):
        super().__init__(name, canvas)
        self.network_manager = NetworkManager.get_instance()
        self.visible = visible
        self.create_server_button = ButtonText(self.canvas, "Create Server", position=("center", "center"), ui_text="Create Server",on_click=self.create_server_button_clicked)
        self.add_ui(self.create_server_button)


    def create_server_button_clicked(self):
        print("Create Server button clicked")
        self.scene.get_object("loading_server").set_active(True)
        self.scene.get_object("create_server").set_active(False)
        self.network_manager.initialize(True) # 始まりそして希望