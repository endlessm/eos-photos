from gi.repository import Gtk

from widgets.option_list import OptionList

class PhotosBlurToolbar(OptionList):
    """
    Widget presenting options for image blurring. Part of the left toolbar.
    """
    def __init__(self, images_path="", **kw):
        super(PhotosBlurToolbar, self).__init__(**kw)
        self._images_path = images_path

        """
        self._no_blur_button = Gtk.RadioButton(label="No Blur")
        self._no_blur_button.connect("toggled", lambda e: self._presenter.on_noblur_toggle(e))
        self._depth_of_field_button = Gtk.RadioButton.new_with_label_from_widget(self._no_blur_button, "Depth of Field Blur")
        self._depth_of_field_button.connect("toggled", lambda e: self._presenter.on_depth_of_field_toggle(e, (0,0)))
        self._tilt_shift_button = Gtk.RadioButton.new_with_label_from_widget(self._depth_of_field_button, label="Tilt Shift Blur")
        self._tilt_shift_button.connect("toggled", lambda e: self._presenter.on_tilt_shift_toggle(e, (0,0)))
        self.pack_start(self._no_blur_button, False, False, 5)
        self.pack_start(self._depth_of_field_button, False, False, 5)
        self.pack_start(self._tilt_shift_button, False, False, 5)

        self.show_all()
        """


    def set_blurs(self, blurs):
        map(self._add_blur_option, blurs)

    def _add_blur_option(self, name_and_thumb):
        blur_name = name_and_thumb[0]
        thumbnail_path = self._images_path + "blur_thumbnails/" + name_and_thumb[1]
        self.add_option("blur", thumbnail_path, blur_name, lambda: self._presenter.on_blur_select(blur_name))
        self.show_all()

    def select_blur(self, blur_name):
        self.select_option(blur_name)

    def set_presenter(self, presenter):
        self._presenter = presenter
