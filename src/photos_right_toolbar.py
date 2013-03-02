from gi.repository import Gtk
from gettext import gettext as _

from widgets.image_text_button import ImageTextButton


class PhotosRightToolbar(Gtk.Alignment):
    """
    The right toolbar with post to facebook and save buttons.
    """
    def __init__(self, images_path="", **kw):
        super(PhotosRightToolbar, self).__init__(xalign=0.5, yalign=0.5, xscale=0.0, yscale=0.0, **kw)

        self._save_button = ImageTextButton(
            normal_path=images_path + "save_normal.png",
            hover_path=images_path + "save_hover.png",
            down_path=images_path + "save_down.png",
            label_text=_("SAVE"),
            name="save-button")
        self._save_button.connect('clicked', lambda w: self._presenter.on_save())

        self._share_button = ImageTextButton(
            normal_path=images_path + "share_normal.png",
            hover_path=images_path + "share_hover.png",
            down_path=images_path + "share_down.png",
            label_text=_("FACEBOOK"),
            name="share-button")
        self._share_button.connect('clicked', lambda w: self._presenter.on_share())

        self._email_button = ImageTextButton(
            normal_path=images_path + "share_normal.png",
            hover_path=images_path + "share_hover.png",
            down_path=images_path + "share_down.png",
            label_text=_("EMAIL"),
            name="email-button")
        self._email_button.connect('clicked', lambda w: self._presenter.on_email())

        self._button_box = Gtk.VBox(homogeneous=False, spacing=20)
        self._button_box.pack_start(self._save_button, expand=False, fill=False, padding=0)
        self._button_box.pack_start(self._share_button, expand=False, fill=False, padding=0)
        self._button_box.pack_start(self._email_button, expand=False, fill=False, padding=0)

        self.add(self._button_box)

        self.show_all()

    def set_presenter(self, presenter):
        self._presenter = presenter
