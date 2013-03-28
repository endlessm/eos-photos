import cairo
from gi.repository import Gtk, Gdk, GdkPixbuf

class PhotosWindow(Gtk.Window):
    __gtype_name__ = 'PhotosWindow'
    # Constants
    TOOLBAR_WIDTH = 180
    PHOTO_HORIZ_PADDING = 35
    PHOTO_VERT_PADDING = 35
    """
    The main window of the photo application. This class handles fullscreen,
    resizing and packs all the toolbars along with with image viewer into its
    allocated space.
    """
    def __init__(self, images_path="", splash_screen=None, photos_top_toolbar=None, left_toolbar=None, right_toolbar=None, image_container=None, **kw):
        kw.setdefault('decorated', False)
        kw.setdefault('window-position', Gtk.WindowPosition.CENTER)
        kw.setdefault('has-resize-grip', False)
        Gtk.Window.__init__(self, **kw)
        self._image_container = image_container
        self._splash_screen = splash_screen
        self._photos_top_toolbar = photos_top_toolbar
        self._left_toolbar = left_toolbar
        self._right_toolbar = right_toolbar

        self._left_toolbar.set_size_request(PhotosWindow.TOOLBAR_WIDTH, -1)
        self._right_toolbar.set_size_request(PhotosWindow.TOOLBAR_WIDTH, -1)

        self._normal_attach = Gtk.Alignment(
            left_padding=PhotosWindow.PHOTO_VERT_PADDING, right_padding=PhotosWindow.PHOTO_VERT_PADDING,
            top_padding=PhotosWindow.PHOTO_VERT_PADDING, bottom_padding=PhotosWindow.PHOTO_VERT_PADDING)
        # self._normal_attach.set_visible_window(False)
        self._normal_attach.add(image_container)
        self._normal_attach.show()

        self._fullscreen_attach = Gtk.EventBox(name="fullscreen-back")
        self._fullscreen_attach.show()

        self._hbox = Gtk.HBox(homogeneous=False, spacing=0)
        self._hbox.pack_start(
            left_toolbar, expand=False, fill=True, padding=0)
        self._hbox.pack_start(
            self._normal_attach, expand=True, fill=True, padding=0)
        self._hbox.pack_end(right_toolbar, expand=False, fill=True, padding=0)
        self._hbox.show()

        self._vbox = Gtk.VBox(homogeneous=False, spacing=0)
        self._vbox.pack_start(self._photos_top_toolbar, expand=False, fill=False, padding=0)
        self._vbox.pack_start(self._hbox, expand=True, fill=True, padding=0)
        self._vbox.show()

        self._notebook = Gtk.Notebook()
        self._notebook.set_show_tabs(False)
        self._notebook.set_show_border(False)
        self._notebook.append_page(self._splash_screen, None)
        self._notebook.append_page(self._vbox, None)
        self._notebook.append_page(self._fullscreen_attach, None)
        self._notebook.show()

        self.add(self._notebook)

        self._back_image = GdkPixbuf.Pixbuf.new_from_file(images_path + "background-tile.jpg")
        self.connect('draw', self._draw)
        self.set_app_paintable(True)

        # Endless applications are fullscreen
        screen = Gdk.Screen.get_default()
        self._resize_to_fullscreen(screen)
        screen.connect('monitors-changed', self._resize_to_fullscreen)
        screen.connect('size-changed', self._resize_to_fullscreen)
        self.connect('key_press_event', self._on_keypress)
        self.connect('destroy', lambda w: Gtk.main_quit())

    def _draw(self, w, cr):
        cr.save()
        Gdk.cairo_set_source_pixbuf(cr, self._back_image, 0, 0)
        cr.get_source().set_extend(cairo.EXTEND_REPEAT)
        cr.paint()
        cr.restore()

    def _on_keypress(self, widget, event):
        if event.keyval == Gdk.KEY_Escape and self.fullscreen:
            self.set_image_fullscreen(False)

    def set_photo_editor_active(self):
        self._notebook.set_current_page(self._notebook.page_num(self._vbox))

    def set_image_fullscreen(self, fullscreen):
        if fullscreen:
            self._notebook.set_current_page(self._notebook.page_num(self._fullscreen_attach))
            self._image_container.reparent(self._fullscreen_attach)
            self._image_container.set_fullscreen_mode(True)
        else:
            self._notebook.set_current_page(self._notebook.page_num(self._vbox))
            self._image_container.reparent(self._normal_attach)
            self._image_container.set_fullscreen_mode(False)

    def _get_screen_dimensions(self):
        # This ought to return the size of the screen, less any panels or
        # docks.
        screen = Gdk.Screen.get_default()
        if screen.get_n_monitors() == 1:
            monitor = 0
        else:
            self.realize()  # so that self.get_window() is not None
            monitor = screen.get_monitor_at_window(self.get_window())
        rect = screen.get_monitor_workarea(monitor)
        return rect.width, rect.height

    def _resize_to_fullscreen(self, screen):
        # When anything about the Gdk.Screen or Gdk.Monitor changes, resize the
        # window to fullscreen.
        width, height = self._get_screen_dimensions()
        # width, height = 800, 600
        self.set_default_size(width, height)
        self.resize(width, height)
        # Might be a better way to do this. But for now, this set_size_request
        # was the best way I could figure out to make sure the window does not
        # shrink to its contents.
        self.set_size_request(width, height)

    def set_presenter(self, presenter):
        self._presenter = presenter
