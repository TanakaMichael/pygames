from core.component.component import Component
from core.component.physics.circle_collider import CircleCollider
class Player(Component):
    def __init__(self, game_object):
        super().__init__(game_object)
        self.game = game_object
        self.score = 0
        self.is_alive = True
        self.event_manager = game_object.event_manager
        self.collider = game_object.get_component(CircleCollider)

        game_object.event_manager.register_event("on_food_eaten", self.on_food_eaten)
        game_object.event_manager.register_event("on_snake_hit_wall", self.on_snake_hit_wall)
    def on_food_eaten(self, snake, food):
        self.score += food.score
        food.destroy()
        print(f"Score: {self.score}")
    def on_snake_hit_wall(self):
        self.is_alive = False
        print("Game Over!")
        print(f"Score: {self.score}")
        self.collider.enabled = False