from gi.repository import Clutter, GLib, Gdk, GObject


class PhotosImageWidget(Clutter.Actor):
    """
    A clutter actor which knows how to display the current model. Composites
    multiple layers of model together with Clutter. Actually a member of the
    model, breaking the MVP paradigm. But interacts closely with model and
    this cuts down on a lot of function passing overhead through the
    presenter.
    """
    def __init__(self, images_path="", **kw):
        kw.setdefault("layout-manager", Clutter.BinLayout())
        super(PhotosImageWidget, self).__init__(**kw)
        self._ratio = 1.0

        self._base_image = Clutter.Texture()
        self.add_child(self._base_image)
        self._border_image = Clutter.Texture()
        self.add_child(self._border_image)

    def get_ratio(self):
        return self._ratio

    def replace_base_image(self, data, width, height):
        Gdk.threads_add_idle(
            GLib.PRIORITY_DEFAULT_IDLE,
            lambda dummy: self._replace_base_image_callback(data, width, height),
            None)

    def _replace_base_image_callback(self, data, width, height):
        self._base_image.set_from_rgb_data(data, False, width, height, 0, 3, 0)
        self._ratio = float(width) / height

    def replace_border_image(self, data, width, height):
        Gdk.threads_add_idle(
            GLib.PRIORITY_DEFAULT_IDLE,
            lambda dummy: self._replace_border_image_callback(data, width, height),
            None)

    def _replace_border_image_callback(self, data, width, height):
        self._border_image.set_from_rgb_data(data, True, width, height, 0, 4, 0)
        self._border_image.show()

    def hide_border_image(self):
        self._border_image.hide()
