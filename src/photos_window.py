from gi.repository import Gtk

class PhotosWindow(Gtk.Window):
    __gtype_name__ = 'PhotosWindow'

    def __init__(self, top_toolbar, left_toolbar, right_toolbar, center_view, **kw):
        # Set our properties on Gtk.Window's constructor, but allow them to be
        # overridden when creating the window.
        kw.setdefault('decorated', False)
        kw.setdefault('window-position', Gtk.WindowPosition.CENTER)
        Gtk.Window.__init__(self, *args, **kw)

        self._hbox = Gtk.HBox(homogeneous=False, spacing=0)
        self._hbox.pack_start(left_toolbar, expand=False, fill=False, padding=0)
        self._hbox.pack_start(center_view, expand=True, fill=True, padding=0)
        self._hbox.pack_start(right_toolbar, expand=False, fill=False, padding=0)
        self._hbox.show_all()

        self._vbox = Gtk.VBox(homogeneous=False, spacing=0)
        self._vbox.pack_start(top_toolbar, expand=False, fill=False, padding=0)
        self._vbox.pack_start(self._hbox, expand=True, fill=True, padding=0)

        self.fullscreen()

    def minimize(self):
        self.iconify()

    def close(self):
        self.destroy()
