from gi.repository import Clutter
from draggable_box import DraggableBox

class CropOverlay(Clutter.Actor):
    def __init__(self, **kw):
        kw.setdefault('x-expand', True)
        kw.setdefault('y-expand', True)
        kw["reactive"] = True
        super(CropOverlay, self).__init__(**kw)

        self._crop_box = DraggableBox(self)

    def show_crop_overlay(self):
        self.show()

    def hide_crop_overlay(self):
        self.hide()

    def resize_crop_box(self, width, height):
        self._crop_box.resize(width, height)

    def get_crop_selection(self, width, height):
        return self._crop_box.get_crop_selection_coordinates(width, height)
