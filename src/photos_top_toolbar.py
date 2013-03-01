from gi.repository import Gtk

from image_button import ImageButton
from image_text_button import ImageTextButton

class PhotosTopToolbar(Gtk.EventBox):
    """
    The top toolbar of the Photo app with open, minimize and close buttons.
    """
    def __init__(self, images_path="", **kw):
        super(PhotosTopToolbar, self).__init__(**kw)
        self.get_style_context().add_class(Gtk.STYLE_CLASS_PRIMARY_TOOLBAR)

        self._close_button = ImageButton(normal_path=images_path + "close_normal.png",
                                         hover_path=images_path + "close_hover.png",
                                         down_path=images_path + "close_down.png",
                                         name="close-button")
        self._close_button.connect('clicked', lambda w: self._presenter.on_close())

        self._minimize_button = ImageButton(normal_path=images_path + "minimize_normal.png",
                                            hover_path=images_path + "minimize_hover.png",
                                            down_path=images_path + "minimize_down.png",
                                            name="minimize-button")
        self._minimize_button.connect('clicked', lambda w: self._presenter.on_minimize())

        self._open_button = ImageTextButton(normal_path=images_path + "OpenButton-icon_normal-hover.png",
                                            hover_path=images_path + "OpenButton-icon_normal-hover.png",
                                            down_path=images_path + "OpenButton-icon_down.png",
                                            label_text=_("OPEN IMAGE"),
                                            name="open-button")
        self._open_button.connect('clicked', lambda w: self._presenter.on_open())

        self._hbox = Gtk.HBox(homogeneous=False, spacing=0)
        self._hbox.pack_start(self._open_button, expand=False, fill=False, padding=20)
        self._hbox.pack_end(self._close_button, expand=False, fill=False, padding=0)
        self._hbox.pack_end(self._minimize_button, expand=False, fill=False, padding=0)

        # This vbox is only to get a few pixels of padding above and below the
        # buttons in the toolbar. Is there a better way to do this?
        self._vbox = Gtk.VBox(homogeneous=False, spacing=0)
        self._vbox.pack_start(self._hbox, expand=False, fill=False, padding=3)

        self.add(self._vbox)

        self.show_all()

    def set_presenter(self, presenter):
        self._presenter = presenter
