from gi.repository import Gtk


class PhotosAdjustmentToolbar(Gtk.VBox):
    """
    Widget presenting sliders for image adjustments. Part of the left toolbar.
    """
    def __init__(self, images_path="", **kw):
        super(PhotosAdjustmentToolbar, self).__init__(homogeneous=False, spacing=0, **kw)

        self._brightness_label = Gtk.Label(name="filter-label", label="Brightness")
        self.pack_start(self._brightness_label, False, False, 0)
        adj1 = Gtk.Adjustment(1.0, 0.0, 2.0, 0.01, 0, 0)
        self._brightness_slider = Gtk.HScale(adjustment=adj1, draw_value=False)
        self._brightness_slider.connect(
            "value-changed", lambda adjust: self._presenter.on_brightness_change(adjust.get_value()))
        self.pack_start(self._brightness_slider, False, False, 5)

        self._contrast_label = Gtk.Label(name="filter-label", label="Contrast")
        self.pack_start(self._contrast_label, False, False, 0)
        adj1 = Gtk.Adjustment(1.0, 0.0, 2.0, 0.01, 0, 0)
        self._contrast_slider = Gtk.HScale(adjustment=adj1, draw_value=False)
        self._contrast_slider.connect(
            "value-changed", lambda adjust: self._presenter.on_contrast_change(adjust.get_value()))
        self.pack_start(self._contrast_slider, False, False, 5)

        self._saturation_label = Gtk.Label(name="filter-label", label="Saturation")
        self.pack_start(self._saturation_label, False, False, 0)
        adj1 = Gtk.Adjustment(1.0, 0.0, 1.0, 0.01, 0, 0)
        self._saturation_slider = Gtk.HScale(adjustment=adj1, draw_value=False)
        self._saturation_slider.connect(
            "value-changed", lambda adjust: self._presenter.on_saturation_change(adjust.get_value()))
        self.pack_start(self._saturation_slider, False, False, 5)

        self.show_all()

    def set_presenter(self, presenter):
        self._presenter = presenter

    def set_brightness_slider(self, value):
        self._brightness_slider.set_value(value)

    def set_contrast_slider(self, value):
        self._contrast_slider.set_value(value)

    def set_saturation_slider(self, value):
        self._saturation_slider.set_value(value)
