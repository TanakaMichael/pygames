class UIElement:
    """すべての UI コンポーネントの基底クラス"""
    def __init__(self, canvas, anchor=(0.5, 0.5), size=(100, 50), position_mode="anchor", color=(255, 255, 255), layer=0, visible=True):
        self.canvas = canvas
        self.anchor = anchor  # (0.0 - 1.0) で画面のどこに配置するか決める
        self.size = size
        self.position_mode = position_mode  # "anchor" または "absolute"
        self.color = color
        self.layer = layer  # **レイヤー**
        self.visible = visible

        self.canvas.add_element(self)  # **Canvas に追加 (自動でソートされる)**

    def get_position(self):
        """カメラのサイズに基づいて UI の描画位置を計算"""
        screen_width, screen_height = self.canvas.get_canvas_size()
        if self.position_mode == "anchor":
            return (int(self.anchor[0] * screen_width - self.size[0] / 2),
                    int(self.anchor[1] * screen_height - self.size[1] / 2))
        return self.anchor  # absolute モードではそのまま座標を返す

    def update(self, delta_time):
        """更新処理 (オーバーライド用)"""
        pass

    def render(self, screen):
        """描画処理 (オーバーライド用)"""
        pass
