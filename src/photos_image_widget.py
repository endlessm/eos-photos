from gi.repository import Clutter, GLib, Gdk, GObject

from crop_overlay import CropOverlay

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

        self._crop_overlay = CropOverlay()
        self.add_child(self._crop_overlay)
        self._crop_overlay.hide_crop_overlay()
        self.crop_overlay_visible = False

        bind_overlay_size = Clutter.BindConstraint(coordinate = Clutter.BindCoordinate.SIZE, source = self._base_image)
        self._crop_overlay.add_constraint(bind_overlay_size)

        self.connect('allocation-changed', self.alloc_changed)

    def get_ratio(self):
        return self._ratio

    def alloc_changed(self, actor, box, flags):
        alloc = self.get_allocation_geometry()
        img_width = alloc.width
        img_height = alloc.height
        self._crop_overlay.resize_crop_box(img_width, img_height)

    def do_get_property(self, property):
        if property.name == "ratio":
            return self._ratio
        else:
            return Clutter.Actor.do_get_property(self, property)
    
    def toggle_crop_overlay(self):
        if self.crop_overlay_visible:
            self.hide_crop_overlay()
        else:
            self.show_crop_overlay()

    def show_crop_overlay(self):
        if not self.crop_overlay_visible:
            self._crop_overlay.show_crop_overlay()
            self.crop_overlay_visible = True

    def hide_crop_overlay(self):
        if self.crop_overlay_visible:
            self._crop_overlay.hide_crop_overlay()
            self.crop_overlay_visible = False

    def get_crop_selection(self, width, height):
        return self._crop_overlay.get_crop_selection(width, height)

    def do_set_property(self, property, value):
        if property.name == "ratio":
            self._ratio = value
        else:
            return Clutter.Actor.do_set_property(self, property, value)

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
