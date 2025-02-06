from core.game_object import GameObject
class Panel(GameObject):
    def __init__(self, name="Panel", canvas=None, visible=False):
        self.uis = {}
        super().__init__(name, visible)
        self.canvas = canvas
    def add_ui(self, ui):
        self.uis[ui.name] = ui
        self.canvas.add_object(ui)
        ui.set_active(self.active)
        return ui

    def remove_ui(self, ui_name):
        if ui_name in self.uis:
            self.canvas.remove_object(self.uis[ui_name])
            del self.uis[ui_name]
    def set_active(self, active):
        super().set_active(active)
        for ui in self.uis.values():
            ui.set_active(active)
        
        