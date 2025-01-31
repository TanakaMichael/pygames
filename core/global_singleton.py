from core.game import Game

class Global:
    """すべてのシングルトンが継承する基底クラス"""
    _instance = None

    @classmethod
    def get_instance(cls):
        """シングルトンインスタンスを取得し、Game に登録"""
        if cls._instance is None:
            cls._instance = cls()
            Game.get_instance().register_component(cls._instance)
        return cls._instance
