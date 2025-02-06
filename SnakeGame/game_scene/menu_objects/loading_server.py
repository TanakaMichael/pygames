import pygame
from core.panel import Panel
from core.UI.object.mesh_text import MeshText
from core.UI.object.mesh_text_btn import ButtonText
from core.UI.object.mesh_list import MeshList
from core.network.network_manager import NetworkManager

class LoadingServer(Panel):
    def __init__(self, canvas, name="loadingServer", visible=False):
        super().__init__(name, canvas)
        self.network_manager = NetworkManager.get_instance()
        self.visible = visible
        self.create_server_button = MeshText(self.canvas, "loading", position=("center", "center"), text="loading...",)
        self.add_ui(self.create_server_button)
