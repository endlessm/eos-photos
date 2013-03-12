from gi.repository import Gtk


class PhotosAdjustmentToolbar(Gtk.VBox):

    def __init__(self, images_path="", **kw):
        super(PhotosAdjustmentToolbar, self).__init__(homogeneous=False, spacing=0, **kw)

        label = Gtk.Label(name="filter-label", label="Contrast")
        self.pack_start(label, False, False, 0)
        adj1 = Gtk.Adjustment(1.0, 0.0, 2.0, 0.01, 0.01, 0.01)
        slider = Gtk.HScale(adjustment=adj1, draw_value=False)
        slider.connect("value-changed", lambda adjust: self._presenter.on_contrast_change(adjust.get_value()))
        self.pack_start(slider, False, False, 5)

        label = Gtk.Label(name="filter-label", label="Brightness")
        self.pack_start(label, False, False, 0)
        adj1 = Gtk.Adjustment(1.0, 0.0, 2.0, 0.01, 0.01, 0.01)
        slider = Gtk.HScale(adjustment=adj1, draw_value=False)
        slider.connect("value-changed", lambda adjust: self._presenter.on_brightness_change(adjust.get_value()))
        self.pack_start(slider, False, False, 5)

        label = Gtk.Label(name="filter-label", label="Saturation")
        self.pack_start(label, False, False, 0)
        adj1 = Gtk.Adjustment(1.0, 0.0, 1.0, 0.01, 0.01, 0.01)
        slider = Gtk.HScale(adjustment=adj1, draw_value=False)
        slider.connect("value-changed", lambda adjust: self._presenter.on_saturation_change(adjust.get_value()))
        self.pack_start(slider, False, False, 5)

        self.show_all()

    def set_presenter(self, presenter):
        self._presenter = presenter
