from gi.repository import Gtk

from image_text_button import ImageTextButton

class PhotosWindow(Gtk.Window):
    __gtype_name__ = 'PhotosWindow'

    def __init__(self, top_toolbar, left_toolbar, right_toolbar, image_viewer, **kw):
        # kw.setdefault('decorated', False)
        kw.setdefault('window-position', Gtk.WindowPosition.CENTER)
        Gtk.Window.__init__(self, **kw)

        self._table = Gtk.Table(1, 24, True)
        self._table.set_row_spacings(10)
        self._table.attach(left_toolbar, 0, 4, 0, 1)
        self._table.attach(right_toolbar, 20, 24, 0, 1)
        self._table.attach(image_viewer, 4, 20, 0, 1)
        self._table.show()

        self._vbox = Gtk.VBox(homogeneous=False, spacing=0)
        self._vbox.pack_start(top_toolbar, expand=False, fill=False, padding=0)
        self._vbox.pack_start(self._table, expand=True, fill=True, padding=0)
        self._vbox.show()
        self.add(self._vbox)

        # Let's just hardcode the resolution of one of our flats for now.
        self.set_size_request(1024, 768)
        # self.fullscreen()

    def minimize(self):
        self.iconify()

    def close(self):
        self.destroy()
