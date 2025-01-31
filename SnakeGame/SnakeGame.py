import pygame
from core.core_initializer import CoreInitializer
from .snake_game_scene import SnakeGameScene

class SnakeGame:
    """スネークゲーム (Slither.io スタイル)"""

    def __init__(self, is_server=False):
        pygame.init()
        self.screen = pygame.display.set_mode((1920, 1080), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.running = True

        # **コアシステムの初期化**
        self.core = CoreInitializer(is_server)
        self.scene_manager = self.core.get_scene_manager()
        self.network_manager = self.core.get_network_manager()
        self.event_manager = self.core.get_event_manager()

        # **シーンのセットアップ**
        self.setup_scenes()

    def setup_scenes(self):
        """ゲームシーンをセットアップ"""
        if self.network_manager.is_server:
            main_scene = SnakeGameScene("MainScene", self.screen)
            self.scene_manager.add_scene(main_scene)
            self.scene_manager.set_active_scene("MainScene")
    def run(self):
        """メインループ"""
        while self.running:
            delta_time = self.clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

            self.screen.fill((0, 0, 0))
            self.scene_manager.update(delta_time)
            self.scene_manager.render(self.screen)
            pygame.display.flip()

        pygame.quit()