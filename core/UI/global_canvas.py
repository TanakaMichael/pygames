class GlobalCanvas(Canvas):
    """ゲーム全体の UI を管理 (設定, ロビー, メニューなど)"""
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(GlobalCanvas, cls).__new__(cls)
            cls._instance.__init__()
        return cls._instance

    def __init__(self):
        super().__init__()
