from gi.repository import Gtk, Gdk, GdkPixbuf, Endless

from drop_shadow_alignment import DropShadowAlignment
from widgets.image_text_button import ImageTextButton


class PhotosWindow(Endless.Window):
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
    def __init__(self, images_path="", splash_screen=None, left_toolbar=None, right_toolbar=None, image_container=None, **kw):
        kw.setdefault('decorated', False)
        kw.setdefault('window-position', Gtk.WindowPosition.CENTER)
        kw.setdefault('has-resize-grip', False)
        Gtk.Window.__init__(self, **kw)
        self._image_container = image_container
        self._splash_screen = splash_screen
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

        self._open_button = ImageTextButton(label=_("OPEN IMAGE"),
                                            image_size_x=21,
                                            image_size_y=19,
                                            name="open-photos-button")
        self._open_button.connect('clicked', lambda w: self._presenter.on_open())
        self._open_button.show_all();

        pm = self.get_page_manager()
        # Splash page
        pm.add(self._splash_screen)
        pm.set_page_background_uri(self._splash_screen, images_path + "background_splash.jpg")
        # Main page
        pm.add(self._hbox)
        pm.set_page_left_topbar_widget(self._hbox, self._open_button)
        pm.set_page_background_uri(self._hbox, images_path + "background-tile.jpg")
        pm.set_page_background_repeats(self._hbox, True)
        pm.set_page_background_size(self._hbox, "auto")
        # Fullscreen page
        pm.add(self._fullscreen_attach)

        self.connect('key_press_event', self._on_keypress)

    def _on_keypress(self, widget, event):
        # We only call set_fullscreen to false if we are on the fullscreen page
        if event.keyval == Gdk.KEY_Escape and self.get_page_manager().get_visible_page() == self._fullscreen_attach:
            self.set_image_fullscreen(False)

    def set_photo_editor_active(self):
        self.get_page_manager().set_visible_page(self._hbox)

    def set_image_fullscreen(self, fullscreen):
        if fullscreen:
            self.get_page_manager().set_visible_page(self._fullscreen_attach)
            self._image_container.reparent(self._fullscreen_attach)
            self._image_container.set_fullscreen_mode(True)
        else:
            self.get_page_manager().set_visible_page(self._hbox)
            self._image_container.reparent(self._normal_attach)
            self._image_container.set_fullscreen_mode(False)

    def set_presenter(self, presenter):
        self._presenter = presenter
