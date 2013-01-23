class PhotosView(object):
    """
    The main view class for the photo application. Mainly just passes the
    presenter calls to the appropriate UI elements. PhotosWindow does the
    actual toplevel layout of the toolbars and central view.
    """
    def __init__(self, presenter):
        self._top_toolbar = PhotosTopToolbar(presenter)
        self._left_toolbar = PhotosLeftToolbar(presenter)
        self._right_toolbar = PhotosRightToolbar(presenter)
        self._image_view = PhotosImageView()
        self._window = PhotosWindow(_top_toolbar, _left_toolbar, _right_toolbar, _image_view)

    def get_window(self):
        return self._window
