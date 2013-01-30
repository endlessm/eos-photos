from gi.repository import Gtk

from image_button import ImageButton
from image_text_button import ImageTextButton

class PhotosTopToolbar(Gtk.EventBox):
    """
    The top toolbar of the Photo app with open, minimize and close buttons.
    """
    def __init__(self, **kw):
        super(PhotosTopToolbar, self).__init__(**kw)
        self.get_style_context().add_class(Gtk.STYLE_CLASS_PRIMARY_TOOLBAR)

        #TODO: nice image path from application like in weather
        self._close_button = ImageButton(normal_path="../images/close_normal.png",
                                         hover_path="../images/close_hover.png",
                                         down_path="../images/close_down.png")
        self._close_button.connect('clicked', lambda w: self._presenter.close())
        self._close_button.show()

        self._minimize_button = ImageButton(normal_path="../images/minimize_normal.png",
                                            hover_path="../images/minimize_hover.png",
                                            down_path="../images/minimize_down.png")
        self._minimize_button.connect('clicked', lambda w: self._presenter.minimize())
        self._minimize_button.show()

        self._open_button = ImageTextButton(normal_path="../images/close_normal.png",
                                            hover_path="../images/close_hover.png",
                                            down_path="../images/close_down.png",
                                            label_text="ABRIR IMAGEN")
        self._open_button.connect('clicked', lambda w: self._presenter.open())
        self._open_button.show()

        self._grid = Gtk.HBox(homogeneous=False, spacing=0)
        self._grid.pack_start(self._open_button, expand=False, fill=False, padding=0)
        self._grid.pack_end(self._close_button, expand=False, fill=False, padding=0)
        self._grid.pack_end(self._minimize_button, expand=False, fill=False, padding=0)
        self.add(self._grid)


    def set_presenter(self, presenter):
        self._presenter = presenter
