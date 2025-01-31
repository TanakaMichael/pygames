import pygame
from core.game import Game
from core.camera import Camera
from core.game_scene import GameScene
from core.network.network_manager import NetworkManager
from core.rigidbody import RigidBody
from core.circle_collider import CircleCollider
from core.ui.canvas import Canvas

from SnakeGame.game_manager import GameManager
from SnakeGame.snake_controller import SnakeController
from SnakeGame.snake_network_sync import SnakeNetworkSync
from SnakeGame.food_manager import FoodManager
# Pygame 初期化
pygame.init()
screen = pygame.display.set_mode((1920, 1080), pygame.RESIZABLE)
clock = pygame.time.Clock()

# **ゲーム & シーン管理**
game = Game()
scene = GameScene("SnakeGame")
network_manager = NetworkManager()
camera = Camera(world_view_size=(1920, 1080))

# **ゲームマネージャー**
game_manager = GameManager()
scene.add_object(game_manager)

# **食べ物管理**
food_manager = FoodManager()
scene.add_object(food_manager)

# **スネーク (プレイヤー)**
player_snake = SnakeNetworkSync("PlayerSnake")
player_snake.add_component(RigidBody(player_snake))
player_snake.add_component(CircleCollider(player_snake, radius=20))
player_snake.add_component(SnakeController(player_snake))
scene.add_object(player_snake)

# **カメラをプレイヤーに追従**
camera.target = player_snake

# **UI**
canvas = Canvas(screen)
scene.add_object(canvas)

# **メインループ**
running = True
while running:
    delta_time = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

    screen.fill((0, 0, 0))
    scene.update(delta_time)
    scene.render(screen)
    pygame.display.flip()

pygame.quit()
