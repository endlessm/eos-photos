from gi.repository import Gtk

from widgets.option_list import OptionList


class PhotosDistortToolbar(OptionList):
    """
    A widget showing a list of clickable distortion options. Part of left toolbar.
    """
    def __init__(self, images_path="", **kw):
        super(PhotosDistortToolbar, self).__init__(**kw)
        self._images_path = images_path

    def set_distortions(self, distortions):
        map(self._add_distort_option, distortions)

    def _add_distort_option(self, name_and_thumb):
        distort_name = name_and_thumb[0]
        thumbnail_path = self._images_path + "distortion_thumbnails/" + name_and_thumb[1]
        self.add_option("filter", thumbnail_path, distort_name, 
            lambda: self._presenter.on_distortion_select(distort_name))
        self.show_all()

    def select_distortion(self, distort_name):
        self.select_option(distort_name)

    def set_presenter(self, presenter):
        self._presenter = presenter