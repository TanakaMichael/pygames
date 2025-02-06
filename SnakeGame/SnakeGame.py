import pygame
from core.core_initializer import CoreInitializer
from .game_scene.snake_game_main import SnakeGameScene
from .game_scene.snake_game_menu import MenuScene
from .game_scene.test_scene import TestScene
import cProfile
class SnakeGame:
    """スネークゲーム (Slither.io スタイル)"""

    def __init__(self, is_server=False):
        pygame.init()
        self.screen = pygame.display.set_mode((1920, 1080), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.running = True

        # **コアシステムの初期化**
        self.core = CoreInitializer()
        self.scene_manager = self.core.get_scene_manager()
        self.network_manager = self.core.get_network_manager()
        self.event_manager = self.core.get_event_manager()

        # **シーンのセットアップ**
        self.setup_scenes()

    def setup_scenes(self):
        """ゲームシーンをセットアップ"""
        main_scene = SnakeGameScene("MainScene", self.screen)
        menu_scene = MenuScene("MenuScene", self.screen)
        test_scene = TestScene("TestScene", self.screen)
        self.scene_manager.add_scene(main_scene)
        self.scene_manager.add_scene(menu_scene)
        self.scene_manager.add_scene(test_scene)
        self.scene_manager.set_active_scene("MenuScene")
    def run(self):
        """メインループ"""
        while self.running:
            delta_time = self.clock.tick(120) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    self.event_manager.trigger_event("resize_screen")
                self.core.handle_event(event)

            self.screen.fill((0, 0, 0))
            self.core.update(delta_time)
            self.core.render(self.screen)
            pygame.display.flip()
        
    
        pygame.quit()