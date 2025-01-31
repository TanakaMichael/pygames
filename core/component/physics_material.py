class PhysicsMaterial:
    """物理マテリアル (摩擦 & 反発係数)"""
    def __init__(self, friction=0.98, bounciness=0.5):
        """
        :param friction: 摩擦係数 (0.0 = 滑る, 1.0 = 摩擦大)
        :param bounciness: 反発係数 (0.0 = 反発なし, 1.0 = 完全反発)
        """
        self.friction = friction
        self.bounciness = bounciness
