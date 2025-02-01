from core.game_object import GameObject
class Panel(GameObject):
    def __init__(self, name="Panel", canvas=None):
        super().__init__(name)
        self.uis = {}
        self.canvas = canvas
    def add_ui(self, ui):
        self.uis[ui.name] = ui
        self.canvas.add_element(ui)
    def remove_ui(self, ui_name):
        if ui_name in self.uis:
            self.canvas.remove_element(self.uis[ui_name])
            del self.uis[ui_name]
    def update(self, dt):
        super().update(dt)
        for ui in self.uis.values():
            ui.update(dt)
        
        