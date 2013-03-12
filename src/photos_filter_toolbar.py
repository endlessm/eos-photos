from gi.repository import Gtk

from widgets.option_list import OptionList


class PhotosFilterToolbar(OptionList):

    def __init__(self, images_path="", **kw):
        super(PhotosFilterToolbar, self).__init__(**kw)
        self._images_path = images_path

    def set_filters(self, filters):
        map(self._add_filter_option, filters)

    def _add_filter_option(self, name_and_thumb):
        filter_name = name_and_thumb[0]
        thumbnail_path = self._images_path + "filter_thumbnails/" + name_and_thumb[1]
        self.add_option("filter", thumbnail_path, filter_name, lambda: self._presenter.on_filter_select(filter_name))
        self.show_all()

    def select_filter(self, filter_name):
        self.select_option(filter_name)

    def set_presenter(self, presenter):
        self._presenter = presenter
