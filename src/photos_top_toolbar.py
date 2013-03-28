from gi.repository import Gtk, Gdk

from top_toolbar import TopToolbar
from widgets.image_button import ImageButton
from widgets.image_text_button import ImageTextButton


class PhotosTopToolbar(TopToolbar):
    """
    The top toolbar of the Photo app with open, minimize and close buttons.
    """
    def __init__(self, images_path="", **kw):
        super(PhotosTopToolbar, self).__init__(images_path=images_path,**kw)

        self._open_button = ImageTextButton(normal_path=images_path + "icon_topbar_OpenPhoto_normal.png",
                                            hover_path=images_path + "icon_topbar_OpenPhoto_hover.png",
                                            down_path=images_path + "icon_topbar_OpenPhoto_normal.png",
                                            label=_("OPEN IMAGE"),
                                            name="open-photos-button")
        self._open_button.connect('clicked', lambda w: self._presenter.on_open())

        self._left_side = Gtk.Alignment(top_padding=4, bottom_padding=3)
        self._left_side.add(self._open_button)

        self.get_toolbar_container().pack_start(self._left_side, expand=False, fill=False, padding=7)

        self.show_all()
