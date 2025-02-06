from SnakeGame.game_scene.test_scene_objects.player import Player
from SnakeGame.game_scene.test_scene_objects.box import Box
from core.scene.game_scene import GameScene
from SnakeGame.game_scene.menu_objects.frame_rate import FrameRate
from core.camera import Camera
from core.map.floor import Floor
from core.map.background import Background
class TestScene(GameScene):
    def __init__(self, name, screen):
        super().__init__(name, screen)
    def start(self):
        self.floor = self.world.add_floor(Floor("1_floor", 1))

    
        self.camera = self.add_camera(Camera(self.canvas))
        #self.camera.add_layer(Background("haikei1", "SnakeGame/assets/pii.png", 0.5, True, True))
        self.floor.add_object(Player(camera=self.camera))
        self.floor.add_object(Box())
        self.add_object(FrameRate(self.canvas, "FrameRate"), True)
        super().start() # すべてのオブジェクトのStartを実行
        