from gi.repository import Gtk

from widgets.option_list import OptionList


class PhotosBorderToolbar(OptionList):
    """
    A widget showing a list of clickable border options. Part of left toolbar.
    """
    def __init__(self, images_path="", **kw):
        super(PhotosBorderToolbar, self).__init__(**kw)
        self._images_path = images_path

    def set_borders(self, borders):
        map(self._add_border_option, borders)

    def _add_border_option(self, name_and_thumb):
        border_name = name_and_thumb[0]
        thumbnail_path = self._images_path + "border_thumbnails/" + name_and_thumb[1]
        self.add_option("filter", thumbnail_path, border_name, lambda: self._presenter.on_border_select(border_name))
        self.show_all()

    def select_border(self, border_name):
        self.select_option(border_name)

    def set_presenter(self, presenter):
        self._presenter = presenter
