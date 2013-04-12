from gi.repository import Gtk


class ToolbarSeparator(Gtk.HBox):
    """
    The separators for our toolbar, draw from two images with cairo.
    """
    def __init__(self, images_path="", **kw):
        super(ToolbarSeparator, self).__init__(**kw)
        self._vbox = Gtk.VBox(homogeneous=False, spacing=0)
        top_image = Gtk.Image.new_from_file(images_path + "separator_black.png")
        self._vbox.pack_start(top_image, expand=False, fill=False, padding=0)
        bottom_image = Gtk.Image.new_from_file(images_path + "separator_white.png")
        self._vbox.pack_start(bottom_image, expand=False, fill=False, padding=0)
        self.pack_start(self._vbox, expand=False, fill=False, padding=0)
