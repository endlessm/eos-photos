from photos_top_toolbar import PhotosTopToolbar
from photos_window import PhotosWindow

class PhotosView(object):
    """
    The main view class for the photo application. Mainly just passes the
    presenter calls to the appropriate UI elements. PhotosWindow does the
    actual toplevel layout of the toolbars and central view.
    """
    def __init__(self):
        self._top_toolbar = PhotosTopToolbar()
        self._window = PhotosWindow(self._top_toolbar)

    def set_presenter(self, presenter):
        self._presenter = presenter
        self._top_toolbar.set_presenter(presenter)

    def get_window(self):
        return self._window
