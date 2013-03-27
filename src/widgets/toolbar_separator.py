from gi.repository import Gtk


class ToolbarSeparator(Gtk.VBox):
    """
    The separators for our toolbar, draw from two images with cairo.
    """
    def __init__(self, images_path="", **kw):
        super(ToolbarSeparator, self).__init__(**kw)
        top_image = Gtk.Image.new_from_file(images_path + "separator_black.png")
        self.pack_start(top_image, expand=False, fill=False, padding=0)
        bottom_image = Gtk.Image.new_from_file(images_path + "separator_white.png")
        self.pack_start(bottom_image, expand=False, fill=False, padding=0)
