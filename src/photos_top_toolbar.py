from gi.repository import Gtk

class PhotosTopToolbar(Gtk.HBox):
    """
    The top toolbar of the Photo app with open, minimize and close buttons.
    """
    def __init__(self):
        super(PhotosTopToolbar, self).__init__()

    def set_presenter(self, presenter):
        self._presenter = presenter
        