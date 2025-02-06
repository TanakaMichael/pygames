from core.map.floor import Floor
class WorldManager:
    def __init__(self, scene):
        self.scene = scene
        self.floors = [] # 一階や二階など

    # === Floor 管理 ===
    def add_floor(self, floor):
        self.floors.append(floor)
        floor.scene = self.scene
        return floor
    def get_floor(self, floor):
        if isinstance(floor, Floor):
            return self.floors.get(floor)
        if isinstance(self, int):
            for floor in self.floors:
                if floor.level is floor:
                    return floor

    def update(self, delta_time):
        # すべての Floor と Layer を更新
        for floor in self.floors:
            floor.update(delta_time)
    def handle_event(self, event):
        # すべての Floor と Layer からイベントを処理
        for floor in self.floors:
            floor.handle_event(event)

    def render(self, camera):
        # === Floor の描画 ===
        for floor in self.floors:
            floor.render(camera)
    def start(self):
        # === 世界の開始 ===
        for floor in self.floors:
            floor.start()
    def end(self):
        # === 世界の終了 ===
        for floor in self.floors:
            floor.end()