# -*- coding: utf-8 -*-
from gi.repository import Gtk

from widgets.option_list import OptionList
from widgets.slider import Slider
from widgets.image_text_button import ImageTextButton
from widgets.image_button import ImageButton


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

    # Should be overridden by subclasses that need it.
    def get_desired_scroll_position(self):
        raise NotImplementedError

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

    def get_desired_scroll_position(self):
        return self._list.get_desired_scroll_position()

class TransformToolbar(CategoryToolbar):
    def __init__(self, **kw):
        kw["name"] = "transform"
        kw.setdefault("left-padding", 10)
        kw.setdefault("right-padding", 15)
        kw.setdefault("top-padding", 10)
        kw.setdefault("bottom-padding", 10)
        kw.setdefault("xscale", 1.0)
        super(TransformToolbar, self).__init__(**kw)
        self._vbox = Gtk.VBox(homogeneous=False, spacing=8)

        self._rotate_button = ImageTextButton(label=_(u"Rotate Right 90\N{Degree Sign}"))
        self._rotate_button.connect("clicked", lambda e: self._presenter.on_rotate())
        self._rotate_button.set_name("rotate-button")

        self._crop_button = CropOptions(images_path=self._images_path)

        self._vbox.pack_start(self._rotate_button, False, False, 0)
        self._vbox.pack_start(self._crop_button, False, False, 0)

        self.add(self._vbox)

    def open_crop_options(self):
        self._crop_button.show_crop_options()

    def close_crop_options(self):
        self._crop_button.hide_crop_options()

    def set_presenter(self, presenter):
        self._crop_button._presenter = presenter
        super(TransformToolbar, self).set_presenter(presenter)

    def get_label(self):
        return _("TRANSFORM")

class CropOptions(Gtk.Frame):
    def __init__(self, images_path, **kw):
        kw["name"] = "crop-options"
        super(CropOptions, self).__init__(**kw)
        self._images_path = images_path
        self._crop_options_box = Gtk.HBox(no_show_all=True)
        self._vbox = Gtk.VBox()

        self._crop_button = ImageTextButton(label=_("Crop"))
        self._crop_button.connect("clicked", self.activate_crop)
        self._crop_button.set_name("crop-button")

        self._crop_label = Gtk.Label()
        self._crop_label.set_label(_("Apply Crop?"))
        self._crop_label.set_name("crop-label")
        self._crop_label.show()
        self._crop_options_box.pack_start(self._crop_label, False, False, 0)

        self._apply_button = ImageButton(
            normal_path = self._images_path + 'confirm_ok-btn_normal.png',
            hover_path = self._images_path + 'confirm_ok-btn_hover.png',
            down_path = self._images_path + 'confirm_ok-btn_pressed.png'
        )
        self._apply_button.connect("clicked", self.apply_crop)
        self._apply_button.set_name("apply-button")
        self._apply_button.show_all()

        self._cancel_button = ImageButton(
            normal_path = self._images_path + 'confirm_cancel-btn_normal.png',
            hover_path = self._images_path + 'confirm_cancel-btn_hover.png',
            down_path = self._images_path + 'confirm_cancel-btn_pressed.png'
        )
        self._cancel_button.connect("clicked", self.cancel_crop)
        self._cancel_button.set_name("cancel-button")
        self._cancel_button.show_all()

        self._crop_options_box.pack_start(self._cancel_button, False, False, 0)
        self._crop_options_box.pack_start(self._apply_button, False, False, 0)

        self._vbox.pack_start(self._crop_button, False, False, 0)
        self._vbox.pack_start(self._crop_options_box, False, False, 0)

        self._style_context = self.get_style_context()
        self._button_context = self._crop_button.get_style_context()
        self._options_state = 'inactive'
        self._style_context.add_class(self._options_state)
        self._button_context.add_class(self._options_state)

        self.add(self._vbox)

    def hide_crop_options(self):
        self._crop_options_box.hide()
        self._button_context.remove_class(self._options_state)
        self._style_context.remove_class(self._options_state)
        self._options_state = 'inactive'
        self._button_context.add_class(self._options_state)
        self._style_context.add_class(self._options_state)

    def show_crop_options(self):
        # Crop overlay is now visible, so a keypress to 'enter'
        # should apply the crop
        self._apply_button.grab_focus()

        self._crop_options_box.show()
        self._button_context.remove_class(self._options_state)
        self._style_context.remove_class(self._options_state)
        self._options_state = 'active'
        self._button_context.add_class(self._options_state)
        self._style_context.add_class(self._options_state)

    def apply_crop(self, event):
        self._presenter.on_crop_apply()

    def activate_crop(self, event):
        self._presenter.on_crop_activate()

    def cancel_crop(self, event):
        self._presenter.on_crop_cancel()

class BlurToolbar(OptionListToolbar):
    def __init__(self, **kw):
        kw["name"] = "blur"
        super(BlurToolbar, self).__init__(**kw)

    def set_blurs(self, blurs):
        self.set_options(blurs)

    def get_label(self):
        return _("BLURS")

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
        return _("BORDERS")

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
        return _("FILTERS")

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
        return _("DISTORT")

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

        self._brightness_label = Gtk.Label(label=_("Brightness"), halign=Gtk.Align.START)
        self._brightness_label.get_style_context().add_class("slider-label")
        brightness_adjust = Gtk.Adjustment(1.0, 0.0, 2.0, 0.01, 0, 0)
        self._brightness_slider = Slider(adjustment=brightness_adjust)
        self._brightness_slider.connect(
            "value-changed", lambda adjust: self._presenter.on_brightness_change(adjust.get_value()))
        self._brightness_slider.connect('key-press-event', lambda w, e: True)
        self._vbox.pack_start(self._brightness_label, False, False, 0)
        self._vbox.pack_start(self._brightness_slider, False, False, 0)

        self._contrast_label = Gtk.Label(label=_("Contrast"), halign=Gtk.Align.START)
        self._contrast_label.get_style_context().add_class("slider-label")
        contrast_adjust = Gtk.Adjustment(1.0, 0.0, 2.0, 0.01, 0, 0)
        self._contrast_slider = Slider(adjustment=contrast_adjust)
        self._contrast_slider.connect(
            "value-changed", lambda adjust: self._presenter.on_contrast_change(adjust.get_value()))
        self._contrast_slider.connect('key-press-event', lambda w, e: True)
        self._vbox.pack_start(self._contrast_label, False, False, 0)
        self._vbox.pack_start(self._contrast_slider, False, False, 0)

        self._saturation_label = Gtk.Label(label=_("Saturation"), halign=Gtk.Align.START)
        self._saturation_label.get_style_context().add_class("slider-label")
        saturation_adjust = Gtk.Adjustment(1.0, 0.0, 2.0, 0.01, 0, 0)
        self._saturation_slider = Slider(adjustment=saturation_adjust)
        self._saturation_slider.connect(
            "value-changed", lambda adjust: self._presenter.on_saturation_change(adjust.get_value()))
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
        return _("ADJUST")
