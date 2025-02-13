from core.component.physics.circle_collider import CircleCollider
from core.component.component import Component
from core.network.network_manager import NetworkManager
from core.global_event_manager import GlobalEventManager

class SnakeCollider(Component):
    def __init__(self, game_object, radius):
        super().__init__(game_object)
        self.collider = game_object.add_component(CircleCollider, radius=radius)

        if not self.collider:
            self.collider = CircleCollider(game_object, radius)
        self.network_manager = NetworkManager.get_instance()

        self.collider.event.register_event("on_collision", self.on_collision)
        
    def on_collision(self, other):
        """衝突時の処理 (Food / Wall)"""
        if other.game_object.name == "Food":
            print(f"🍏 {self.game_object.name} が Food を取得!")
            # **サーバーでスコア加算 & 食べ物再生成**
            if self.network_manager.is_server:
                self.game_object.event_manager.trigger_event("on_food_eaten", snake=self.game_object, food=other.game_object)

        elif other.game_objectr.name == "Wall":
            print(f"❌ {self.game_object.name} が壁に衝突!")
            
            # **サーバーでゲームオーバー処理**
            self.game_object.event_manager.trigger_event("on_snake_hit_wall", snake=self.game_object)