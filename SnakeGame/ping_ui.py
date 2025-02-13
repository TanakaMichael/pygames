from core.game_object import GameObject
from core.panel import Panel
from core.UI.elements.text import Text
from core.network.network_manager import NetworkManager
import pygame
class PingUI(Panel):
    def __init__(self, name="PingUI", canvas=None):
        super().__init__(name, canvas)
        self.text = Text(canvas=canvas, name="Ping",position=pygame.Vector2(100, 100))
        self.join_user = Text(canvas=canvas, name="users",position=pygame.Vector2(20, 20), position_mode="absolute")
        self.add_ui(self.text)
        self.add_ui(self.join_user)
        self.network_manager = NetworkManager.get_instance()
    def update(self, dt):
        super().update(dt)
        self.text.text = f"Ping: {self.network_manager.ping_rate}"
        self.join_user.text = "Users: "  # 初期化
        for user in self.network_manager.get_clients_name():
            self.join_user.text += f"{user}, "
