from gi.repository import Gtk

from widgets.option_list import OptionList


class CategoryToolbar(Gtk.Alignment):
    """
    Base class for a catagory widget in the left toolbar. Can have any
    content, but must display provide a label and icon in normal and hover
    states.
    """
    def __init__(self, images_path="", **kw):
        kw.setdefault("xalign", 0.0)
        kw.setdefault("yalign", 0.0)
        kw.setdefault("xscale", 0.0)
        kw.setdefault("yscale", 0.0)
        super(CategoryToolbar, self).__init__(**kw)
        self._images_path = images_path

    def set_presenter(self, presenter):
        self._presenter = presenter

    def get_label(self):
        return _("Untitled")

class OptionListToolbar(CategoryToolbar):
    """
    A widget showing a list of clickable options.
    """
    def __init__(self, **kw):
        kw.setdefault("left-padding", 30)
        super(OptionListToolbar, self).__init__(**kw)
        self._list = OptionList()
        self._callback = lambda: None
        self.add(self._list)
        self.show_all()

    def set_options(self, options):
        map(self._set_option, options)

    def _set_option(self, name_and_thumb):
        option_name = name_and_thumb[0]
        thumbnail_path = self._images_path + self.get_thumbnail_prefix() + name_and_thumb[1]
        self._list.add_option(thumbnail_path, option_name, lambda: self.clicked_callback(option_name))
        self.show_all()

    def select(self, option):
        self._list.select_option(option)

    def get_thumbnail_prefix(self):
        return ""

    def clicked_callback(self, option_name):
        pass

class BlurToolbar(OptionListToolbar):
    def __init__(self, **kw):
        kw["name"] = "blur"
        super(BlurToolbar, self).__init__(**kw)

    def set_blurs(self, blurs):
        self.set_options(blurs)

    def get_label(self):
        return _("Blurs")

    def get_thumbnail_prefix(self):
        return "blur_thumbnails/"

    def clicked_callback(self, blur_name):
        self._presenter.on_blur_select(blur_name)


class BorderToolbar(OptionListToolbar):
    """
    A widget showing a list of borders. Part of left toolbar.
    """
    def __init__(self, **kw):
        kw["name"] = "border"
        super(BorderToolbar, self).__init__(**kw)

    def get_label(self):
        return _("Borders")

    def get_thumbnail_prefix(self):
        return "border_thumbnails/"

    def clicked_callback(self, option_name):
        self._presenter.on_border_select(option_name)


class FilterToolbar(OptionListToolbar):
    """
    A widget showing a list of filters. Part of left toolbar.
    """
    def __init__(self, **kw):
        kw["name"] = "filter"
        super(FilterToolbar, self).__init__(**kw)

    def get_label(self):
        return _("Filters")

    def get_thumbnail_prefix(self):
        return "filter_thumbnails/"

    def clicked_callback(self, option_name):
        self._presenter.on_filter_select(option_name)


class DistortToolbar(OptionListToolbar):
    """
    A widget showing a list of filters. Part of left toolbar.
    """
    def __init__(self, **kw):
        kw["name"] = "distort"
        super(DistortToolbar, self).__init__(**kw)

    def get_label(self):
        return _("Distortions")

    def get_thumbnail_prefix(self):
        return "distortion_thumbnails/"

    def clicked_callback(self, option_name):
        self._presenter.on_distortion_select(option_name)


class AdjustmentToolbar(CategoryToolbar):
    """
    Widget presenting sliders for image adjustments. Part of the left toolbar.
    """
    def __init__(self, images_path="", **kw):
        kw["name"] = "adjustment"
        kw.setdefault("left-padding", 10)
        kw.setdefault("right-padding", 15)
        kw.setdefault("top-padding", 10)
        kw.setdefault("bottom-padding", 10)
        kw.setdefault("xscale", 1.0)
        super(AdjustmentToolbar, self).__init__(**kw)
        self._vbox = Gtk.VBox(homogeneous=False, spacing=0)

        self._brightness_label = Gtk.Label(label=_("Brightness"))
        self._brightness_label.get_style_context().add_class("slider-label")
        brightness_adjust = Gtk.Adjustment(1.0, 0.0, 2.0, 0.01, 0, 0)
        self._brightness_slider = Gtk.HScale(adjustment=brightness_adjust, draw_value=False)
        self._brightness_slider.connect(
            "value-changed", lambda adjust: self._presenter.on_brightness_change(adjust.get_value()))
        self._brightness_slider.connect('button-release-event', lambda w, e: self._presenter.on_slider_release())
        self._brightness_slider.connect('key-press-event', lambda w, e: True)
        self._vbox.pack_start(self._brightness_label, False, False, 0)
        self._vbox.pack_start(self._brightness_slider, False, False, 0)

        self._contrast_label = Gtk.Label(label=_("Contrast"))
        self._contrast_label.get_style_context().add_class("slider-label")
        contrast_adjust = Gtk.Adjustment(1.0, 0.0, 2.0, 0.01, 0, 0)
        self._contrast_slider = Gtk.HScale(adjustment=contrast_adjust, draw_value=False)
        self._contrast_slider.connect(
            "value-changed", lambda adjust: self._presenter.on_contrast_change(adjust.get_value()))
        self._contrast_slider.connect('button-release-event', lambda w, e: self._presenter.on_slider_release())
        self._contrast_slider.connect('key-press-event', lambda w, e: True)
        self._vbox.pack_start(self._contrast_label, False, False, 0)
        self._vbox.pack_start(self._contrast_slider, False, False, 0)

        self._saturation_label = Gtk.Label(label=_("Saturation"))
        self._saturation_label.get_style_context().add_class("slider-label")
        saturation_adjust = Gtk.Adjustment(1.0, 0.0, 2.0, 0.01, 0, 0)
        self._saturation_slider = Gtk.HScale(adjustment=saturation_adjust, draw_value=False)
        self._saturation_slider.connect(
            "value-changed", lambda adjust: self._presenter.on_saturation_change(adjust.get_value()))
        self._saturation_slider.connect('button-release-event', lambda w, e: self._presenter.on_slider_release())
        self._saturation_slider.connect('key-press-event', lambda w, e: True)
        self._vbox.pack_start(self._saturation_label, False, False, 0)
        self._vbox.pack_start(self._saturation_slider, False, False, 0)

        self.add(self._vbox)
        self.show_all()

    def set_brightness_slider(self, value):
        self._brightness_slider.set_value(value)

    def set_contrast_slider(self, value):
        self._contrast_slider.set_value(value)

    def set_saturation_slider(self, value):
        self._saturation_slider.set_value(value)

    def get_label(self):
        return _("Adjust")
