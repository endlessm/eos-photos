from gi.repository import Gtk, Gdk, GdkPixbuf

from widgets.image_text_button import ImageTextButton


class WrappingLabel(Gtk.Label):
    """
    Label for the splash screen.
    """
    def __init__(self, width=0, **kw):
        super(WrappingLabel, self).__init__(wrap=True, **kw)
        self._width = width

    def do_get_preferred_width(self):
        if self._width != 0:
            return self._width, self._width
        return Gtk.Label.do_get_preferred_width()


class SplashScreen(Gtk.EventBox):
    MINIMUM_HEIGHT = 37 # Set this minimum height of the toolbar to 37 to prevent size changes
                        # when switching to the photo editor.

    def __init__(self, splash_top_toolbar=None, images_path=None, **kw):
        super(SplashScreen, self).__init__(**kw)

        self._splash_top_toolbar = splash_top_toolbar

        self._splash_top_toolbar.set_size_request(-1, SplashScreen.MINIMUM_HEIGHT)

        self._splash_open_button = ImageTextButton(normal_path=images_path + "icon_topbar_OpenPhoto_hover.png",
                                            hover_path=images_path + "icon_topbar_OpenPhoto_hover.png",
                                            down_path=images_path + "icon_topbar_OpenPhoto_hover.png",
                                            label=_("Open Image"),
                                            name="splash-open-photos-button")
        self._splash_open_button.connect('clicked', lambda w: self._presenter.on_open())

        splash_label = WrappingLabel(width=600, label=_("Choose one of your photos to begin!"), name="splash-label", expand=False)
        splash_label.set_alignment(0, 0)
        splash_label.set_margin_bottom(10)

        # These hboxes are used to prevent GTK from ignoring expand flags and auto-expanding the
        # button and label to the maximum window width.
        label_hbox = Gtk.HBox()
        label_hbox.pack_start(splash_label, expand=False, fill=False, padding=0)

        button_hbox = Gtk.HBox()
        button_hbox.pack_start(self._splash_open_button, expand=False, fill=False, padding=0)

        splash_container = Gtk.VBox()
        splash_container.set_margin_left(60)
        splash_container.set_margin_top(65)
        splash_container.pack_start(label_hbox, expand=False, fill=False, padding=0)
        splash_container.pack_start(button_hbox, expand=False, fill=False, padding=0)

        self._splash_vbox = Gtk.VBox(expand=False)
        self._splash_vbox.pack_start(self._splash_top_toolbar, expand=False, fill=False, padding=0)
        self._splash_vbox.pack_start(splash_container, expand=False, fill=False, padding=0)

        self.add(self._splash_vbox)

    def set_presenter(self, presenter):
        self._presenter = presenter
