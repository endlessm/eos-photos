from gi.repository import Gtk

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
            label=_("SAVE"),
            name="save-button",
            vertical=True)
        self._save_button.connect('clicked', lambda w: self._presenter.on_save())

        self._share_button = ImageTextButton(
            normal_path=images_path + "facebook_normal.png",
            hover_path=images_path + "facebook_hover.png",
            down_path=images_path + "facebook_down.png",
            label=_("FACEBOOK"),
            name="share-button",
            vertical=True)
        self._share_button.connect('clicked', lambda w: self._presenter.on_share())

        # self._email_button = ImageTextButton(
        #     normal_path=images_path + "email_normal.png",
        #     hover_path=images_path + "email_hover.png",
        #     down_path=images_path + "email_down.png",
        #     label=_("EMAIL"),
        #     name="email-button",
        #     vertical=True)
        # self._email_button.connect('clicked', lambda w: self._presenter.on_email())

        self._button_box = Gtk.VBox(homogeneous=False, spacing=20)
        self._button_box.pack_start(self._save_button, expand=False, fill=False, padding=0)
        self._button_box.pack_start(self._share_button, expand=False, fill=False, padding=0)
        # self._button_box.pack_start(self._email_button, expand=False, fill=False, padding=0)

        self.add(self._button_box)

        self.set_vexpand(True)

    def set_presenter(self, presenter):
        self._presenter = presenter
