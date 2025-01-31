class NetworkObjectFactory:
    """ネットワークオブジェクトの生成を管理"""
    registered_classes = {}

    @staticmethod
    def register_class(cls):
        """クラスを登録"""
        NetworkObjectFactory.registered_classes[cls.__name__] = cls

    @staticmethod
    def create_object(class_name, steam_id, network_id):
        """登録されたクラスからオブジェクトを作成"""
        if class_name in NetworkObjectFactory.registered_classes:
            return NetworkObjectFactory.registered_classes[class_name](network_id, steam_id)
        else:
            print(f"⚠ `{class_name}` は未登録")
            return None
