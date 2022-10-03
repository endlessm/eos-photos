import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Endless, Gtk, Gio

from .widgets.image_text_button import ImageTextButton


class PhotosRightToolbar(Gtk.VBox):
    """
    The right toolbar with post to facebook and save buttons.
    """

    def __init__(self, **kw):
        super(PhotosRightToolbar, self).__init__(homogeneous=False, vexpand=True, **kw)

        vmargin = 40
        if Endless.is_composite_tv_screen(None):
            vmargin = 10

        self._open_photo_button = ImageTextButton(
            image_size_x=ImageTextButton.SIZE_MEDIUM,
            image_size_y=ImageTextButton.SIZE_MEDIUM,
            halign=Gtk.Align.CENTER,
            margin_top=vmargin,
            margin_bottom=15,
            label=_("OPEN PHOTO"),
            name="open-photo-button",
            vertical=True)
        self._open_photo_button.connect('clicked', lambda w: self._presenter.on_open())

        self._save_button = ImageTextButton(
            image_size_x=ImageTextButton.SIZE_MEDIUM,
            image_size_y=ImageTextButton.SIZE_MEDIUM,
            halign=Gtk.Align.CENTER,
            margin_bottom=15,
            label=_("SAVE"),
            name="save-button",
            vertical=True)
        self._save_button.connect('clicked', lambda w: self._presenter.on_save())

        self._bg_button = ImageTextButton(
            image_size_x=ImageTextButton.SIZE_MEDIUM,
            image_size_y=ImageTextButton.SIZE_MEDIUM,
            halign=Gtk.Align.CENTER,
            label=_("BACKGROUND"),
            name="wallpaper-button",
            vertical=True)
        self._bg_button.connect('clicked', lambda w: self._presenter.on_set_background())

        self._revert_image_button = ImageTextButton(
            image_size_x=ImageTextButton.SIZE_MEDIUM,
            image_size_y=ImageTextButton.SIZE_MEDIUM,
            halign=Gtk.Align.CENTER,
            margin_top=15,
            margin_bottom=vmargin,
            label=_("REVERT IMAGE"),
            name="revert-image-button",
            vertical=True)
        self._revert_image_button.connect('clicked', lambda w: self._presenter.on_revert())

        inner_button_box = Gtk.VBox(homogeneous=False, spacing=0)
        self.pack_start(self._open_photo_button, expand=False, fill=False, padding=0)
        inner_button_box.pack_start(self._save_button, expand=False, fill=False, padding=0)

        if self._display_share_button():
            self._share_button = ImageTextButton(
                image_size_x=ImageTextButton.SIZE_MEDIUM,
                image_size_y=ImageTextButton.SIZE_MEDIUM,
                halign=Gtk.Align.CENTER,
                margin_bottom=15,
                label=_("FACEBOOK"),
                name="share-button",
                vertical=True)
            self._share_button.connect('clicked', lambda w: self._presenter.on_share())
            inner_button_box.pack_start(self._share_button, expand=False, fill=False, padding=0)

        inner_button_box.pack_start(self._bg_button, expand=False, fill=False, padding=0)
        self.pack_start(inner_button_box, expand=True, fill=False, padding=0)
        self.pack_end(self._revert_image_button, expand=False, fill=False, padding=0)

        self.set_vexpand(True)

    def _display_share_button(self):
        settings = Gio.Settings('com.endlessm.photos')
        return settings.get_boolean('share')

    def set_presenter(self, presenter):
        self._presenter = presenter
