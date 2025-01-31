import pygame
from .component import Component

class Transform(Component):
    """
    位置、スケール、回転を管理する Transform コンポーネント。
    - position: pygame.Vector2
    - scale: pygame.Vector2
    - rotation: pygame.Vector3 (2Dゲームの場合は rotation.z を回転角に使うことが多い)
    """
    def __init__(self, game_object, position=(0, 0), scale=(1, 1), rotation=(0, 0, 0)):
        super().__init__(game_object)
        self.position = pygame.Vector2(position)
        self.scale = pygame.Vector2(scale)
        self.rotation = pygame.Vector3(rotation)  # 2Dゲームでは z成分を使用

    def set_position(self, x, y):
        self.position.x = x
        self.position.y = y

    def set_scale(self, sx, sy):
        self.scale.x = sx
        self.scale.y = sy

    def set_rotation(self, rx, ry, rz):
        """2Dの場合 rz を回転角とみなすことが多い"""
        self.rotation.x = rx
        self.rotation.y = ry
        self.rotation.z = rz

    def get_position(self):
        return self.position

    def get_scale(self):
        return self.scale

    def get_rotation(self):
        """2Dの場合 rotation.z を使用"""
        return self.rotation
