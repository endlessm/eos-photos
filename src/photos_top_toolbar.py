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
                                         down_path="../images/close_down.png",
                                         name="close-button")
        self._close_button.connect('clicked', lambda w: self._presenter.close())

        self._minimize_button = ImageButton(normal_path="../images/minimize_normal.png",
                                            hover_path="../images/minimize_hover.png",
                                            down_path="../images/minimize_down.png",
                                            name="minimize-button")
        self._minimize_button.connect('clicked', lambda w: self._presenter.minimize())

        self._open_button = ImageTextButton(normal_path="../images/close_normal.png",
                                            hover_path="../images/close_hover.png",
                                            down_path="../images/close_down.png",
                                            label_text="ABRIR IMAGEN",
                                            name="open-button")
        self._open_button.connect('clicked', lambda w: self._presenter.open())

        self._hbox = Gtk.HBox(homogeneous=False, spacing=0)
        self._hbox.pack_start(self._open_button, expand=False, fill=False, padding=20)
        self._hbox.pack_end(self._close_button, expand=False, fill=False, padding=0)
        self._hbox.pack_end(self._minimize_button, expand=False, fill=False, padding=0)

        # This vbox is only to get a few pixels of padding above and below the
        # buttons in the toolbar. Is there a better way to do this?
        self._vbox = Gtk.VBox(homogeneous=False, spacing=0)
        self._vbox.pack_start(self._hbox, expand=False, fill=False, padding=3)
        self._vbox.show_all()

        self.add(self._vbox)

    def set_presenter(self, presenter):
        self._presenter = presenter
