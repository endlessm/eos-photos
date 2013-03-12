from gi.repository import Gtk


class PhotosAdjustments(Gtk.VBox):

    def __init__(self, change_callback):
        super(PhotosAdjustments, self).__init__(homogeneous=False, spacing=0)

        label = Gtk.Label(name="filter-label", label="Contrast")
        self.pack_start(label, False, False, 0)
        adj1 = Gtk.Adjustment(1.0, 0.0, 2.0, 0.01, 0.01, 0.01)
        slider = Gtk.HScale(adjustment=adj1)
        slider.connect("value-changed", self._contrast_on_changed, "Contrast")
        self.pack_start(slider, False, False, 0)

        label = Gtk.Label(name="filter-label", label="Brightness")
        self.pack_start(label, False, False, 0)
        adj1 = Gtk.Adjustment(1.0, 0.0, 2.0, 0.01, 0.01, 0.01)
        slider = Gtk.HScale(adjustment=adj1)
        slider.connect("value-changed", self._contrast_on_changed, "Brightness")
        self.pack_start(slider, False, False, 0)

        label = Gtk.Label(name="filter-label", label="Saturation")
        self.pack_start(label, False, False, 0)
        adj1 = Gtk.Adjustment(1.0, 0.0, 1.0, 0.01, 0.01, 0.01)
        slider = Gtk.HScale(adjustment=adj1)
        slider.connect("value-changed", self._contrast_on_changed, "Saturation")
        self.pack_start(slider, False, False, 0)

        self._change_callback = change_callback
        self.show_all()

    def _contrast_on_changed(self, scale, adjust):
        self._change_callback(adjust, scale.get_value())
