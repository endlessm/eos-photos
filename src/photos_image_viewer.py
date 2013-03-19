from gi.repository import Gtk, GdkPixbuf, GtkClutter, Clutter

from widgets.clutter_image_button import ClutterImageButton


class ImageViewer(Gtk.AspectFrame):
    """
    Sizes the image to fit centered in the space allotted. Expands to take up
    any available space. Image embedded with Clutter.
    """
    def __init__(self, images_path="", **kw):
        super(ImageViewer, self).__init__(obey_child=False, ratio=1.0, **kw)
        self._embed = GtkClutter.Embed.new()
        self._embed.connect('size-allocate', self._on_embed_size_allocate)
        self._stage = self._embed.get_stage()

        self._image = Clutter.Texture()
        self._image.add_constraint(Clutter.AlignConstraint(
            align_axis=Clutter.AlignAxis.BOTH, factor=0.5, source=self._stage))
        self._stage.add_child(self._image)

        self._border_image = Clutter.Texture()
        self._border_image.add_constraint(Clutter.AlignConstraint(
            align_axis=Clutter.AlignAxis.BOTH, factor=0.5, source=self._stage))
        self._border_image.hide()
        self._stage.add_child(self._border_image)

        self._fullscreen_button = ClutterImageButton(
            normal_path=images_path + "expand-image_normal.png",
            hover_path=images_path + "expand-image_hover.png",
            down_path=images_path + "expand-image_down.png",
            name="fullscreen-button")
        self._fullscreen_button.add_constraint(Clutter.AlignConstraint(
            align_axis=Clutter.AlignAxis.BOTH, factor=1.0, source=self._stage))
        self._fullscreen_button.get_click_action().connect('clicked', lambda w, e: self._presenter.on_fullscreen())

        self._unfullscreen_button = ClutterImageButton(
            normal_path=images_path + "expand-image-close_normal.png",
            hover_path=images_path + "expand-image-close_hover.png",
            down_path=images_path + "expand-image-close_down.png",
            name="fullscreen-button")
        self._unfullscreen_button.add_constraint(Clutter.AlignConstraint(
            align_axis=Clutter.AlignAxis.BOTH, factor=1.0, source=self._stage))
        self._unfullscreen_button.get_click_action().connect('clicked', lambda w, e: self._presenter.on_unfullscreen())

        self.set_fullscreen_mode(False)

        self.set_hexpand(True)
        self.set_vexpand(True)
        self.add(self._embed)
        self.show()

    def set_fullscreen_mode(self, fullscreen):
        self._fullscreen_mode = fullscreen
        if fullscreen:
            self._stage.add_child(self._unfullscreen_button)
            if self._fullscreen_button.get_parent() == self._stage:
                self._stage.remove_child(self._fullscreen_button)
        else:
            self._stage.add_child(self._fullscreen_button)
            if self._unfullscreen_button.get_parent() == self._stage:
                self._stage.remove_child(self._unfullscreen_button)
        self.queue_resize()

    def _on_embed_size_allocate(self, widget, allocation):
        image_width = allocation.width
        image_height = allocation.height
        self._image.set_size(image_width, image_height)
        self._border_image.set_size(image_width, image_height)

    def replace_base_image_from_data(self, data, width, height):
        self._image.set_from_rgb_data(data, True, width, height, 0, 4, 0)
        self.set_property("ratio", float(width)/height)
        self._embed.show_all()

    def replace_border_image_from_data(self, data, width, height):
        self._border_image.set_from_rgb_data(data, True, width, height, 0, 4, 0)
        self._border_image.show()
        self._embed.show_all()

    def hide_border_image(self):
        self._border_image.hide()

    def set_presenter(self, presenter):
        self._presenter = presenter
