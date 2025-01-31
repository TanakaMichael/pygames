class LocalCanvas(Canvas):
    """ゲームプレイ専用 UI を管理 (体力, スタミナ, ロビー情報など)"""
    def __init__(self, camera):
        super().__init__(camera)
