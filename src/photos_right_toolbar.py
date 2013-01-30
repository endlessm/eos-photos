from gi.repository import Gtk

class PhotosRightToolbar(Gtk.Alignment):
    """
    The right toolbar with post to facebook and save buttons.
    """
    def __init__(self, **kw):
        super(PhotosRightToolbar, self).__init__(xalign=0.5, yalign=0.5, xscale=0.0, yscale=0.0, **kw)
        # TODO: Replace with proper buttons!
        save_image = Gtk.Image.new_from_file("../images/save_normal.png")
        share_image = Gtk.Image.new_from_file("../images/share_normal.png")
        button_box = Gtk.VBox(homogeneous=False, spacing=20)
        button_box.pack_start(save_image, expand=False, fill=False, padding=0)
        button_box.pack_start(share_image, expand=False, fill=False, padding=0)
        self.add(button_box)

    def set_presenter(self, presenter):
        self._presenter = presenter
