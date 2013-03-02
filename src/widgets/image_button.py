from gi.repository import Gtk, GdkPixbuf


class ImageButton(Gtk.Button):
    """
    This is a button for the top toolbar. It contains an image which changes to
    another image when the mouse hovers over it.

    This class is a temporary measure, in order to get the weather app out the
    door. It should not be added permanently to the SDK. Instead, we will use
    named icon sets from the Endless icon theme.
    """
    __gtype_name__ = 'EndlessImageButton'

    def __init__(self, normal_path=None, hover_path=None, down_path=None, **kw):
        kw.setdefault('relief', Gtk.ReliefStyle.NONE)
        Gtk.Button.__init__(self, **kw)

        self._normal_icon_pixbuf = GdkPixbuf.Pixbuf.new_from_file(normal_path)
        self._hover_icon_pixbuf = GdkPixbuf.Pixbuf.new_from_file(hover_path)
        self._down_icon_pixbuf = GdkPixbuf.Pixbuf.new_from_file(down_path)

        self._image = Gtk.Image.new_from_pixbuf(self._normal_icon_pixbuf)
        self.add(self._image)
        self.connect('enter-notify-event', self._on_mouse_enter)
        self.connect('leave-notify-event', self._on_mouse_leave)
        self.connect('button-press-event', self._on_button_press)
        self.connect('button-release-event', self._on_button_release)

    def _on_mouse_enter(self, event, data=None):
        self._image.set_from_pixbuf(self._hover_icon_pixbuf)
        return False  # don't block event

    def _on_mouse_leave(self, event, data=None):
        self._image.set_from_pixbuf(self._normal_icon_pixbuf)
        return False  # don't block event

    def _on_button_press(self, event, data=None):
        self._image.set_from_pixbuf(self._down_icon_pixbuf)
        return False

    def _on_button_release(self, event, data=None):
        self._image.set_from_pixbuf(self._hover_icon_pixbuf)
        return False
