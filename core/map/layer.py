import pygame

class Layer:
    """背景、オブジェクト、近景などを管理するレイヤークラス"""
    def __init__(self, name, parallax_factor=1.0, visible=True):
        """
        :param name: レイヤー名
        :param parallax_factor: パララックス効果の強さ (0.5 = 背景用, 1.0 = 通常, >1.0 = 近景)
        :param visible: レイヤーの表示/非表示
        """
        self.name = name
        self.parallax_factor = parallax_factor
        self.visible = visible
        self.objects = []  # このレイヤーに存在するオブジェクトのリスト
    def create_object(self, path, size=None):
        """オブジェクトをレイ��ーに追加する"""
        obj = pygame.image.load(path)
        if size:
            obj = pygame.transform.scale(obj, pygame.Vector2(size))
        self.add_object(obj)
    def add_object(self, obj):
        """オブジェクトをレイヤーに追加"""
        self.objects.append(obj)

    def remove_object(self, obj):
        """オブジェクトをレイヤーから削除"""
        if obj in self.objects:
            self.objects.remove(obj)

    def update(self, delta_time):
        """レイヤー内のオブジェクトを更新"""
        for obj in self.objects:
            if hasattr(obj, "update"):
                obj.update(delta_time)

    def render(self, surface, camera):
        """レイヤー内のオブジェクトを描画"""
        if not self.visible:
            return

        # パララックスオフセットの計算
        camera_pos = camera.transform.local_position
        parallax_offset = camera_pos * (1 - self.parallax_factor)

        for obj in self.objects:
            if not obj.visible:
                continue

            # カメラ位置を考慮して描画
            obj_screen_pos = camera.world_to_screen(obj.transform.global_position - parallax_offset)
            obj.render(surface, obj_screen_pos)
