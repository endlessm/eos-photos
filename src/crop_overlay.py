from gi.repository import Clutter
from draggable_box import DraggableBox

class CropOverlay(Clutter.Actor):
    def __init__(self, **kw):
        kw["reactive"] = True
        super(CropOverlay, self).__init__(**kw)

        self._crop_box = DraggableBox(self)

    def show_crop_overlay(self):
        self.show()

    def hide_crop_overlay(self):
        self.hide()

    def resize_crop_box(self, stage_width, stage_height):
        self.set_width(stage_width)
        self.set_height(stage_height)
        self._crop_box.resize(stage_width, stage_height)

    def rotate_crop_box(self):
        self._crop_box.rotate_dimensions()

    def reset_crop_box(self):
        self._crop_box.reset_dimensions()

    def get_crop_selection(self, width, height):
        return self._crop_box.get_crop_selection_coordinates(width, height)
