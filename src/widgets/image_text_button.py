from gi.repository import Gtk, GdkPixbuf, Gdk


class ImageTextButton(Gtk.Button):
    """
    This button contains an image and text, packed vertically or horizontally.
    State flags are set on label for css highlighting.

    This class is a temporary measure, in order to get the weather app out the
    door. It should not be added permanently to the SDK. Instead, we will use
    named icon sets from the Endless icon theme.
    """
    __gtype_name__ = 'EndlessImageTextButton'

    def __init__(self,
                 normal_path=None,
                 hover_path=None,
                 down_path=None,
                 label="",
                 vertical=False,
                 **kw):
        Gtk.Button.__init__(self, **kw)

        self._normal_icon_pixbuf = GdkPixbuf.Pixbuf.new_from_file(normal_path)
        self._hover_icon_pixbuf = GdkPixbuf.Pixbuf.new_from_file(hover_path)
        self._down_icon_pixbuf = GdkPixbuf.Pixbuf.new_from_file(down_path)

        self._label_text = label

        self._image = Gtk.Image.new_from_pixbuf(self._normal_icon_pixbuf)
        self._label = Gtk.Label(self._label_text)

        if vertical:
            self._box = Gtk.VBox(homogeneous=False, spacing=0)
        else:
            self._box = Gtk.HBox(homogeneous=False, spacing=0)
        self._box.pack_start(self._image, expand=False, fill=False, padding=0)
        self._box.pack_start(self._label, expand=False, fill=False, padding=2)
        self.add(self._box)

        self.connect('enter-notify-event', self._on_mouse_enter)
        self.connect('leave-notify-event', self._on_mouse_leave)
        self.connect('button-press-event', self._on_button_press)
        self.connect('button-release-event', self._on_button_release)

    def _on_mouse_enter(self, event, data=None):
        flags = self._label.get_state_flags() | Gtk.StateFlags.PRELIGHT
        self._label.set_state_flags(flags, True)
        self._image.set_from_pixbuf(self._hover_icon_pixbuf)
        return False  # don't block event

    def _on_mouse_leave(self, event, data=None):
        flags = Gtk.StateFlags(self._label.get_state_flags() & ~Gtk.StateFlags.PRELIGHT)
        self._label.set_state_flags(flags, True)
        self._image.set_from_pixbuf(self._normal_icon_pixbuf)
        return False  # don't block event

    def _on_button_press(self, event, data=None):
        flags = self._label.get_state_flags() | Gtk.StateFlags.SELECTED
        self._label.set_state_flags(flags, True)
        self._image.set_from_pixbuf(self._down_icon_pixbuf)
        return False

    def _on_button_release(self, event, data=None):
        flags = Gtk.StateFlags(self._label.get_state_flags() & ~Gtk.StateFlags.SELECTED)
        self._label.set_state_flags(flags, True)
        self._image.set_from_pixbuf(self._hover_icon_pixbuf)
        return False
