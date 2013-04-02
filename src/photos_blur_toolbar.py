from gi.repository import Gtk

from widgets.option_list import OptionList

class PhotosBlurToolbar(OptionList):
    """
    Widget presenting options for image blurring. Part of the left toolbar.
    """
    def __init__(self, images_path="", **kw):
        super(PhotosBlurToolbar, self).__init__(**kw)
        self._images_path = images_path

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
