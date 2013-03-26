from gi.repository import Gtk, Gdk

from widgets.image_button import ImageButton
from widgets.image_text_button import ImageTextButton


class TopToolbar(Gtk.EventBox):
    """
    The top toolbar of the Photo app with open, minimize and close buttons.
    """
    def __init__(self, images_path="", **kw):
        super(TopToolbar, self).__init__(**kw)
        self.get_style_context().add_class(Gtk.STYLE_CLASS_PRIMARY_TOOLBAR)

        self._close_button = ImageButton(normal_path=images_path + "top-bar_close_normal.png",
                                         hover_path=images_path + "top-bar_close_hover.png",
                                         down_path=images_path + "top-bar_close_down.png",
                                         name="close-button")
        self._close_button.connect('clicked', lambda w: self._presenter.on_close())

        self._minimize_button = ImageButton(normal_path=images_path + "top-bar_minimize_normal.png",
                                            hover_path=images_path + "top-bar_minimize_hover.png",
                                            down_path=images_path + "top-bar_minimize_down.png",
                                            name="minimize-button")
        self._minimize_button.connect('clicked', lambda w: self._presenter.on_minimize())

        self._right_side = Gtk.HBox(homogeneous=False, spacing=0)
        self._right_side.pack_start(self._minimize_button, expand=False, fill=False, padding=0)
        self._right_side.pack_start(self._close_button, expand=False, fill=False, padding=0)

        self._hbox = Gtk.HBox(homogeneous=False, spacing=0)
        self._hbox.pack_end(self._right_side, expand=False, fill=False, padding=10)

        self.add(self._hbox)

        self.show_all()

    def set_presenter(self, presenter):
        self._presenter = presenter

    def get_toolbar_container(self):
        return self._hbox
