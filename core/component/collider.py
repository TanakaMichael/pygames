from .component import Component

class Collider(Component):
    """当たり判定の基底クラス"""

    def __init__(self, owner):
        super().__init__(owner)

    def check_collision(self, other):
        """他の Collider との当たり判定 (継承クラスで実装)"""
        raise NotImplementedError

    def update(self, delta_time):
        """すべての他の Collider との衝突をチェック"""
        super().update(delta_time)

    def on_collision(self, other):
        """衝突時の処理 (オーバーライド可能)"""
        print(f"Collision detected: {self.owner.name} <-> {other.owner.name}")
