from core.game_object import GameObject
from core.panel import Panel
from core.UI.text import Text
from core.network.network_manager import NetworkManager
import pygame
class PingUI(Panel):
    def __init__(self, name="PingUI", canvas=None):
        super().__init__(name, canvas)
        self.text = Text(canvas=canvas, name="Ping", font_size=30,position=pygame.Vector2(100, 100))
        self.add_ui(self.text)
        self.network_manager = NetworkManager.get_instance()
    def update(self, dt):
        super().update(dt)
        self.text.text = f"Ping: {self.network_manager.ping_rate}"
