from core.network.network_game_object import NetworkGameObject
from core.network.network_object_factory import NetworkObjectFactory
from core.component.transform import Transform
from core.component.sprite import SpriteRenderer
import pygame
class Food(NetworkGameObject):
    """食べ物 (スネークが食べる)"""
    def __init__(self, position, network_id=None):
        super().__init__("Food")
        self.transform = self.add_component(Transform, position=position)
        self.sprite = self.add_component(SpriteRenderer, image_path="SnakeGame/assets/food.png")
        self.transform.position = pygame.Vector2(position)
        if network_id:
            self.network_id = network_id

# **自動で NetworkObjectFactory に登録**
NetworkObjectFactory.register_class(Food)