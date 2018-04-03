from gi.repository import Gtk

from .widgets.image_text_button import ImageTextButton


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


class SplashScreen(Gtk.Grid):
    def __init__(self, **kw):
        super(SplashScreen, self).__init__(margin_start=60, margin_top=65, **kw)

        self._splash_open_button = ImageTextButton(label=(_("Open Image")).upper(),
                                                   image_size_x=21, # Icon x-dimension
                                                   image_size_y=17, # Icon y-dimension
                                                   halign=Gtk.Align.START,
                                                   valign=Gtk.Align.START,
                                                   name="splash-open-photos-button")
        self._splash_open_button.connect('clicked', lambda w: self._presenter.on_open())
        self.attach(self._splash_open_button, 0, 1, 1, 1)

        splash_label = WrappingLabel(width=600, margin_bottom=10,
                                     label=_("Choose one of your photos to begin!"),
                                     name="splash-label",
                                     xalign=0, yalign=0,
                                     valign=Gtk.Align.START,
                                     halign=Gtk.Align.START)
        self.attach(splash_label, 0, 0, 1, 1)

    def set_presenter(self, presenter):
        self._presenter = presenter
