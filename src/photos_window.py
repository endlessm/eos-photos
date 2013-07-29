from gi.repository import Gtk, Gdk, GdkPixbuf
from drop_shadow_alignment import DropShadowAlignment


class PhotosWindow(Gtk.Window):
    __gtype_name__ = 'PhotosWindow'
    # Constants
    TOOLBAR_WIDTH = 180
    PHOTO_HORIZ_PADDING = 35
    PHOTO_VERT_PADDING = 35
    DROP_SHADOW_WIDTH = 7
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

        self._normal_attach = DropShadowAlignment(
            shadowed_widget=self._image_container.get_child(), left_padding=PhotosWindow.PHOTO_HORIZ_PADDING,
            right_padding=PhotosWindow.PHOTO_HORIZ_PADDING, top_padding=PhotosWindow.PHOTO_VERT_PADDING,
            bottom_padding=PhotosWindow.PHOTO_VERT_PADDING)

        self._normal_attach.add(self._image_container)

        # Send a draw signal to due alignment widget to make sure it draws its drop shadow
        # when the size allocation occurs and never before the allocation.
        self._image_container.connect("size-allocate", lambda w, e: self._normal_attach.queue_draw())

        self._fullscreen_attach = Gtk.EventBox(name="fullscreen-back")

        self._hbox = Gtk.HBox(homogeneous=False, spacing=0)
        self._hbox.pack_start(
            left_toolbar, expand=False, fill=True, padding=0)
        self._hbox.pack_start(
            self._normal_attach, expand=True, fill=True, padding=0)
        self._hbox.pack_end(right_toolbar, expand=False, fill=True, padding=0)

        self._vbox = Gtk.VBox(homogeneous=False, spacing=0)
        self._vbox.pack_start(self._photos_top_toolbar, expand=False, fill=False, padding=0)
        self._vbox.pack_start(self._hbox, expand=True, fill=True, padding=0)

        self._notebook = Gtk.Notebook()
        self._notebook.set_show_tabs(False)
        self._notebook.set_show_border(False)
        self._notebook.append_page(self._splash_screen, None)
        self._notebook.append_page(self._vbox, None)
        self._notebook.append_page(self._fullscreen_attach, None)

        self.add(self._notebook)

        self.connect('key_press_event', self._on_keypress)

    def _on_keypress(self, widget, event):
        # Fullscreen page is index number 2.  We only call set_fullscreen to
        # false if we are on the fullscreen page
        if event.keyval == Gdk.KEY_Escape and self._notebook.get_current_page() == 2:
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

    def set_presenter(self, presenter):
        self._presenter = presenter
