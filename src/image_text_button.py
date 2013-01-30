from gi.repository import Gtk, GdkPixbuf, Gdk


class ImageTextButton(Gtk.Button):
    """
    This is a button for the top toolbar. It contains an image which changes to
    another image when the mouse hovers over it.

    This class is a temporary measure, in order to get the weather app out the
    door. It should not be added permanently to the SDK. Instead, we will use
    named icon sets from the Endless icon theme.
    """
    __gtype_name__ = 'EndlessImageTextButton'

    def __init__(self, normal_path=None, hover_path=None, down_path=None, label_text="",
                 normal_font_color=Gdk.RGBA(0.44, 0.44, 0.44, 1), hover_font_color=Gdk.RGBA(0.82, 0.82, 0.82, 1.0),
                 down_font_color=Gdk.RGBA(0.46, 0.46, 0.46, 1), **kw):
        Gtk.Button.__init__(self, **kw)

        self._normal_icon_pixbuf = GdkPixbuf.Pixbuf.new_from_file(normal_path)
        self._hover_icon_pixbuf = GdkPixbuf.Pixbuf.new_from_file(hover_path)
        self._down_icon_pixbuf = GdkPixbuf.Pixbuf.new_from_file(down_path)

        self._label_text = label_text
        self._normal_font_color = normal_font_color
        self._hover_font_color = hover_font_color
        self._down_font_color = down_font_color

        self._image = Gtk.Image.new_from_pixbuf(self._normal_icon_pixbuf)
        self._label = Gtk.Label(self._label_text)
        self._label.override_color(Gtk.StateFlags.NORMAL, normal_font_color)

        self._hbox = Gtk.HBox(homogeneous=False, spacing=0)
        self._hbox.pack_start(self._image, expand=False, fill=False, padding=0)
        self._hbox.pack_start(self._label, expand=False, fill=False, padding=2)
        self.add(self._hbox)

        self.connect('enter-notify-event', self._on_mouse_enter)
        self.connect('leave-notify-event', self._on_mouse_leave)
        self.connect('button-press-event', self._on_button_press)
        self.connect('button-release-event', self._on_button_release)

    def _on_mouse_enter(self, event, data=None):
        self._image.set_from_pixbuf(self._hover_icon_pixbuf)
        self._label.override_color(Gtk.StateFlags.NORMAL, self._hover_font_color)
        return False  # don't block event

    def _on_mouse_leave(self, event, data=None):
        self._image.set_from_pixbuf(self._normal_icon_pixbuf)
        self._label.override_color(Gtk.StateFlags.NORMAL, self._normal_font_color)
        return False  # don't block event

    def _on_button_press(self, event, data=None):
        self._image.set_from_pixbuf(self._down_icon_pixbuf)
        self._label.override_color(Gtk.StateFlags.NORMAL, self._down_font_color)
        return False

    def _on_button_release(self, event, data=None):
        self._image.set_from_pixbuf(self._hover_icon_pixbuf)
        self._label.override_color(Gtk.StateFlags.NORMAL, self._hover_font_color)
        return False
