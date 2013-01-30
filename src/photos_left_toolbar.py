from gi.repository import Gtk

class PhotosLeftToolbar(Gtk.VBox):
    """
    The left filter selection toolbar for the photo app.
    """
    def __init__(self, **kw):
        super(PhotosLeftToolbar, self).__init__(**kw)
        filters_image = Gtk.Image.new_from_file("../images/Filters_title.png")
        filters_image_allign = Gtk.Alignment(xalign=0.5, yalign=0.0, xscale=1.0, yscale=0.0)
        filters_image_allign.add(filters_image)
        self.pack_start(filters_image_allign, expand=False, fill=False, padding=20)

    def set_presenter(self, presenter):
        self._presenter = presenter
