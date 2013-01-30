from gi.repository import Gtk

from photos_top_toolbar import PhotosTopToolbar
from photos_left_toolbar import PhotosLeftToolbar
from photos_right_toolbar import PhotosRightToolbar
from photos_window import PhotosWindow

class PhotosView(object):
    """
    The main view class for the photo application. Mainly just passes the
    presenter calls to the appropriate UI elements. PhotosWindow does the
    actual toplevel layout of the toolbars and central view.
    """
    def __init__(self):
        self._top_toolbar = PhotosTopToolbar()
        self._left_toolbar = PhotosLeftToolbar()
        self._right_toolbar = PhotosRightToolbar()
        self._image = Gtk.Image(file="../images/test_photo.jpg", name="photo-image")
        self._window = PhotosWindow(self._top_toolbar, self._left_toolbar, self._right_toolbar, self._image)

    def set_presenter(self, presenter):
        self._presenter = presenter
        self._top_toolbar.set_presenter(presenter)
        self._left_toolbar.set_presenter(presenter)

    def get_window(self):
        return self._window

    def close_window(self):
        self._window.destroy()

    def minimize_window(self):
        self._window.iconify()

    def replace_image(self, image):
        cur_image = self._window._image_align.get_children()[0]
        self._window._image_align.remove(cur_image)
        self._window._image_align.add(image)
        image.show()
        #self._window._image_align.get_children()[0].show()
