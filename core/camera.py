import pygame

class Camera:
    def __init__(self, target=None, world_view_size=(1920, 1080)):
        """
        :param target: 追跡するオブジェクト
        :param world_view_size: どの解像度でも共通のワールド表示範囲
        """
        self.target = target
        self.world_view_size = pygame.Vector2(world_view_size)
        self.position = pygame.Vector2(0, 0)
        self.screen_size = pygame.Vector2(pygame.display.get_window_size())  # 初期値

    def update(self, delta_time):
        """ターゲットを追跡してカメラ位置を更新"""
        if self.target:
            self.position.x = self.target.transform.position.x - self.world_view_size.x // 2
            self.position.y = self.target.transform.position.y - self.world_view_size.y // 2

    def to_screen_position(self, world_position):
        """
        ワールド座標をスクリーン座標に変換 (カメラ基準 & 解像度対応)
        """
        screen_width, screen_height = pygame.display.get_window_size()
        scale_x = screen_width / self.world_view_size.x
        scale_y = screen_height / self.world_view_size.y

        screen_x = (world_position.x - self.position.x) * scale_x
        screen_y = (world_position.y - self.position.y) * scale_y
        return pygame.Vector2(screen_x, screen_y)

    def to_screen_scale(self, world_scale):
        """
        ワールドスケールをスクリーンスケールに変換 (解像度対応)
        """
        screen_width, screen_height = pygame.display.get_window_size()
        scale_x = screen_width / self.world_view_size.x
        scale_y = screen_height / self.world_view_size.y
        return pygame.Vector2(world_scale.x * scale_x, world_scale.y * scale_y)

