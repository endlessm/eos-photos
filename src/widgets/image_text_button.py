import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf, Gdk
from .composite_button import CompositeButton

class ImageTextButton(Gtk.Button, CompositeButton):
    """
    This button contains an image and text, packed vertically or horizontally.
    State flags are set on label for css highlighting.

    This class is a temporary measure, in order to get the weather app out the
    door. It should not be added permanently to the SDK. Instead, we will use
    named icon sets from the Endless icon theme.
    """
    __gtype_name__ = 'EndlessImageTextButton'
    SIZE_SMALL = 21
    SIZE_MEDIUM = 48
    SIZE_LARGE = 68

    def __init__(self,
                 image_size_x=SIZE_SMALL,
                 image_size_y=SIZE_SMALL,
                 label="",
                 vertical=False,
                 **kw):
        Gtk.Button.__init__(self, **kw)

        self._frame = Gtk.Frame()
        self._frame.get_style_context().add_class("image-frame")
        self._frame.set_size_request(image_size_x, image_size_y)
        sensitive_children = [self._frame]

        if vertical:
            self._box = Gtk.VBox(homogeneous=False, spacing=0)
        else:
            self._box = Gtk.HBox(homogeneous=False, spacing=0)
        align = Gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0.0, yscale=0.0)
        align.add(self._frame)
        self._box.pack_start(align, expand=False, fill=False, padding=0)
        if label:
            self._label = Gtk.Label(label)
            self._box.pack_start(self._label, expand=False, fill=False, padding=2)
            sensitive_children.append(self._label)
        self.add(self._box)

        self.set_sensitive_children(sensitive_children)
