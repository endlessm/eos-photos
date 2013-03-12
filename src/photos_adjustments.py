from gi.repository import Gtk


class PhotosAdjustments(Gtk.VBox):
    MIN = 0.0
    MAX = 2.0
    MID = 1.0

    def __init__(self, change_callback):
        super(PhotosAdjustments, self).__init__(homogeneous=False, spacing=0)

        adjusts = ["Contrast", "Brightness", "Sharpness"]

        for adjust in adjusts:
            self._label = Gtk.Label(name="filter-label", label=adjust)
            self.pack_start(self._label, False, False, 0)
            adj1 = Gtk.Adjustment(self.MID, self.MIN, self.MAX, 0.01, 0.01, 0.01)
            self.slider = Gtk.HScale(adjustment=adj1)
            self.slider.connect("value-changed", self._contrast_on_changed, adjust)
            self.pack_start(self.slider, False, False, 0)

        self._change_callback = change_callback

        self.show_all()

    def _contrast_on_changed(self, scale, adjust):
        self._change_callback(adjust, scale.get_value())

