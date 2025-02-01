from core.network.network_game_object import NetworkGameObject
from core.network.network_object_factory import NetworkObjectFactory
from core.component.transform import Transform
from core.component.sprite import SpriteRenderer
from core.network.network_transform import NetworkTransform
import pygame
class Food(NetworkGameObject):
    """食べ物 (スネークが食べる)"""
    def __init__(self, network_id=None, steam_id=-1, position=pygame.Vector2(0, 0)):
        super().__init__("Food", steam_id=steam_id, network_id=network_id)
        self.transform = self.add_component(Transform, position=position)
        self.sprite = self.add_component(SpriteRenderer, image_path="SnakeGame/assets/food.png")
        self.network_transform = self.add_component(NetworkTransform)
        self.transform.position = pygame.Vector2(position)

# **自動で NetworkObjectFactory に登録**
NetworkObjectFactory.register_class(Food)