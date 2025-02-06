import pygame
from core.game_object import GameObject
from core.component.transform import Transform
from core.coroutine import Coroutine, WaitForSeconds
import math

def ease_out_quad(t):
    return 1 - (1 - t) ** 2  # 加速して減速する自然な動き

def ease_in_out_sine(t):
    return 0.5 * (1 - math.cos(math.pi * t))  # 滑らかな開始と終了

def linear(t):
    return t  # 直線的な動き（デフォルト）

class Camera(GameObject):
    """ワールド座標の一部を切り取って描画する Camera クラス (重心基準 + ズーム対応)"""
    def __init__(self, canvas, name="Camera", view_size=(800, 600), view_canvas_size=None, zoom=1.0, parent=None):
        """
        :param canvas: 描画先の `Canvas`
        :param view_size: **ワールド座標でのカメラの視界範囲 (視界サイズ)**
        :param view_canvas_size: **Canvas 内での描画範囲 (None なら全体に描画)**
        :param zoom: **ズーム倍率**
        """
        super().__init__(name, parent)
        self.canvas = canvas
        self.view_size = pygame.Vector2(view_size)  # **ワールド座標での視界サイズ**
        self.canvas_size = self.canvas.get_canvas_size()  # **Canvas の全体サイズ**
        self.view_canvas_size = pygame.Rect((0, 0), self.canvas_size) if view_canvas_size is None else pygame.Rect(view_canvas_size)
        self.zoom = zoom  # **ズーム倍率**
        self.floor_level = 1  # ✅ 現在の階層
        self.floor_objects = {}  # {floor_level: [objects]}
        # ✅ 追尾用の変数
        self.target = None
        self.follow_speed = 5.0
        self.easing_function = linear  # デフォルトはリニア

        self.render_objects = []

        self.layers = []
    # ✅ フロアごとのオブジェクト登録
    def register_object(self, obj, floor_level):
        """オブジェクトを指定したフロアに登録（重複防止）"""
        # ✅ フロアが未登録なら初期化
        if floor_level not in self.floor_objects:
            self.floor_objects[floor_level] = set()  # **リストからセットに変更**

        # ✅ 既に存在しない場合のみ追加
        if obj not in self.floor_objects[floor_level]:
            self.floor_objects[floor_level].add(obj)  # **セットなら重複防止が簡単**



    # ✅ フロアごとのスケールを計算
    def get_floor_scale(self, floor_level):
        distance = abs(self.floor_level - floor_level)
        scale_factor = max(0.5, 1.0 - 0.2 * distance)  # 近いフロアほど1.0に近いスケール
        return scale_factor
    def set_target(self, target_object, follow_speed=5.0, easing_function=None):
        """🎯 追尾するターゲットを設定"""
        self.target = target_object
        self.follow_speed = follow_speed
        self.easing_function = easing_function or ease_in_out_sine  # ✅ イージング関数を指定可能
        #self.start_follow_coroutine()

    def start_follow_coroutine(self):
        """📦 追尾コルーチン開始"""
        if self.target:
            self.coroutine_manager.start_coroutine(self._follow_target)

    def _follow_target(self):
        """🚀 ターゲット追尾コルーチン"""
        while self.target:
            delta_time = yield WaitForSeconds(0.01)

            current_pos = self.transform.local_position
            target_pos = self.target.transform.global_position

            distance = (target_pos - current_pos).length()
            if distance < 0.1:
                continue  # 微小な移動は無視して最適化

            # ✅ イージング適用
            t = min(1.0, delta_time * self.follow_speed)
            eased_t = self.easing_function(t)
            new_pos = current_pos.lerp(target_pos, eased_t)

            self.transform.set_local_position(new_pos)
    def world_to_screen(self, world_position):
        """
        ワールド座標をスクリーン座標に変換
        - カメラの `Transform` を **中心基準** に `view_size` の範囲を描画
        - `view_canvas_size` 内に描画するようスケーリング
        """
        view_w, view_h = self.view_size
        center_x, center_y = self.transform.get_local_position()  # **カメラの中心**

        # **カメラの視界の左上 (開始座標)**
        view_x = center_x - (view_w / 2) / self.zoom
        view_y = center_y - (view_h / 2) / self.zoom

        # **ワールド座標 → スクリーン座標 (Canvas内の`view_canvas_size` に合わせる)**
        screen_x = ((world_position.x - view_x) / (view_w / self.zoom)) * self.view_canvas_size.width + self.view_canvas_size.x
        screen_y = ((world_position.y - view_y) / (view_h / self.zoom)) * self.view_canvas_size.height + self.view_canvas_size.y
        return pygame.Vector2(screen_x, screen_y)

    def screen_to_world(self, screen_position):
        """
        スクリーン座標をワールド座標に変換
        - `world_to_screen()` の逆変換
        """
        view_w, view_h = self.view_size
        center_x, center_y = self.transform.get_local_position()  # **カメラの中心**

        # **カメラの視界の左上 (開始座標)**
        view_x = center_x - (view_w / 2) / self.zoom
        view_y = center_y - (view_h / 2) / self.zoom

        # **スクリーン座標 → ワールド座標 (Canvas内の`view_canvas_size` を考慮)**
        world_x = ((screen_position.x - self.view_canvas_size.x) / self.view_canvas_size.width) * (view_w / self.zoom) + view_x
        world_y = ((screen_position.y - self.view_canvas_size.y) / self.view_canvas_size.height) * (view_h / self.zoom) + view_y
        return pygame.Vector2(world_x, world_y)

    def get_world_to_screen_scale(self):
        """ワールド座標をスクリーン座標に変換するスケールを取得 (`view_canvas_size` を考慮)"""
        scale_x = self.view_canvas_size.width / (self.view_size.x / self.zoom)
        scale_y = self.view_canvas_size.height / (self.view_size.y / self.zoom)
        return pygame.Vector2(scale_x, scale_y)

    def set_zoom(self, new_zoom):
        """ズーム倍率を変更"""
        self.zoom = max(0.1, new_zoom)  # **0.1 未満にならないように制限**
    def render_parallax(self, surface, layer_object, parallax_factor):
        """パララックス（視差効果）を適用してレイヤーを描画"""
        # カメラの位置に基づいてレイヤーの位置を計算
        camera_pos = self.transform.local_position
        parallax_offset = camera_pos * (1 - parallax_factor)
    
        # 背景画像をループして表示
        bg_image = layer_object.image
        bg_width, bg_height = bg_image.get_size()
    
        # カメラの表示範囲を埋めるようにタイル状に描画
        start_x = -parallax_offset.x % bg_width - bg_width
        start_y = -parallax_offset.y % bg_height - bg_height
    
        for x in range(int(start_x), self.view_canvas_size.width, bg_width):
            for y in range(int(start_y), self.view_canvas_size.height, bg_height):
                surface.blit(bg_image, (x, y))
    def add_layer(self, layer):
        """Layerクラスを継承したものを追加"""
        self.layers.append(layer)

    def render_scene(self, screen):
        if not self.active:
            return

        camera_surface = pygame.Surface(self.view_canvas_size.size, pygame.SRCALPHA)

        # ✅ **1. 背景レイヤー (parallax_factor <= 1.0) を先に描画**
        for layer in sorted(self.layers, key=lambda l: l.parallax_factor):
            if layer.parallax_factor <= 1.0:
                layer.render(camera_surface, self)

        # 2️⃣ 各フロアごとのオブジェクト描画
        for floor_level in sorted(self.floor_objects.keys(), reverse=False):  # ✅ 下の階から描画
            scale = self.get_floor_scale(floor_level)
            for obj in self.floor_objects[floor_level]:
                if obj.visible:
                    screen_pos = self.world_to_screen(obj.transform.global_position)
                    obj.render(camera_surface, screen_pos, scale=scale)  # ✅ スケール適用

        # ✅ **3. 近景レイヤー (parallax_factor > 1.0) を後に描画**
        for layer in sorted(self.layers, key=lambda l: l.parallax_factor):
            if layer.parallax_factor > 1.0:
                layer.render(camera_surface, self)

        screen.blit(camera_surface, self.view_canvas_size.topleft)
