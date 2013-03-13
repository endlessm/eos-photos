from gi.repository import Gtk

from widgets.option_list import OptionList


class PhotosBorderToolbar(OptionList):
    """
    A widget showing a list of clickable border options. Part of left toolbar.
    """
    def __init__(self, images_path="", **kw):
        super(PhotosBorderToolbar, self).__init__(**kw)
        self._images_path = images_path
        self._add_border_option("NONE")
        self._add_border_option("FRAME")
        self._add_border_option("POLARIOD")
        self._add_border_option("BEVELED")
        self.select_border("NONE")

    def _add_border_option(self, label):
        thumbnail_path = self._images_path + "Filters_Example-Picture_01.jpg"
        self.add_option(
            "filter", thumbnail_path, label,
            lambda: self._presenter.on_border_select(label))
        self.show_all()

    def select_border(self, border_name):
        self.select_option(border_name)

    def set_presenter(self, presenter):
        self._presenter = presenter
