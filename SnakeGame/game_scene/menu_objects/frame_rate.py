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
class FrameRate(Panel):
    def __init__(self, canvas, name="PingUI", visible = True):
        FONT_PATH = "KH-Dot-Dougenzaka-12.ttf"
        super().__init__(name, canvas, visible)
        self.frame_rate = MeshText(canvas, "frome_rate",font_path=FONT_PATH, font_ratio=0.05,position=("right-175", "top+100"))
        self.add_ui(self.frame_rate)
        self.alpha = 0.1  # 移動平均の重み (1 に近いほど最新値を重視)
        self.fps_smooth = 0.0  # 移動平均の fps

    def update(self, dt):
        super().update(dt)
        if dt > 0:
            instant_fps = 1.0 / dt
            self.fps_smooth = (self.alpha * instant_fps) + ((1 - self.alpha) * self.fps_smooth)
            self.frame_rate.set_text(f"{self.fps_smooth:.2f}f/s")