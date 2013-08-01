from gi.repository import Gtk, GdkPixbuf, GtkClutter, Clutter

from widgets.clutter_image_button import ClutterImageButton


class ImageContainer(Gtk.AspectFrame):
    """
    Sizes the image to fit centered in the space allotted. Expands to take up
    any available space. Image embedded with Clutter.
    """
    def __init__(self, images_path="", **kw):
        super(ImageContainer, self).__init__(obey_child=False, ratio=1.0, **kw)
        self._embed = GtkClutter.Embed.new()
        self._stage = self._embed.get_stage()

        self._fullscreen_button = ClutterImageButton(
            normal_path=images_path + "expand-image_normal.png",
            hover_path=images_path + "expand-image_hover.png",
            down_path=images_path + "expand-image_down.png",
            name="fullscreen-button",
            depth=1.0)  # Always draw over the attached image widget
        self._fullscreen_button.add_constraint(Clutter.AlignConstraint(
            align_axis=Clutter.AlignAxis.BOTH, factor=1.0, source=self._stage))
        self._fullscreen_button.get_click_action().connect('clicked', lambda w, e: self._presenter.on_fullscreen())

        self._unfullscreen_button = ClutterImageButton(
            normal_path=images_path + "expand-image-close_normal.png",
            hover_path=images_path + "expand-image-close_hover.png",
            down_path=images_path + "expand-image-close_down.png",
            name="fullscreen-button",
            depth=1.0)  # Always draw over the attached image widget
        self._unfullscreen_button.add_constraint(Clutter.AlignConstraint(
            align_axis=Clutter.AlignAxis.BOTH, factor=1.0, source=self._stage))
        self._unfullscreen_button.get_click_action().connect('clicked', lambda w, e: self._presenter.on_unfullscreen())

        self.set_fullscreen_mode(False)

        self.set_hexpand(True)
        self.set_vexpand(True)
        self.add(self._embed)

    def set_image_widget(self, image_widget):
        self._stage.add_child(image_widget)
        image_widget.add_constraint(Clutter.BindConstraint(
            coordinate=Clutter.BindCoordinate.SIZE, source=self._stage))
        image_widget.connect("notify::ratio", self._ratio_changed)
        self._image_widget = image_widget

    def _ratio_changed(self, widget, property):
        self.set_property("ratio", self._image_widget.get_property("ratio"))
        # TODO: we are using the ratio changed signal to detect when to show
        # the clutter stage for the first time. And that's hella hacky

    def set_fullscreen_mode(self, fullscreen):
        self._fullscreen_mode = fullscreen
        # We may bring the fullscreen back someday so for now I'm removing the
        # code that adds the fullscreen button to the scene

        # if fullscreen:
        #     self._stage.add_child(self._unfullscreen_button)
        #     if self._fullscreen_button.get_parent() == self._stage:
        #         self._stage.remove_child(self._fullscreen_button)
        # else:
        #     self._stage.add_child(self._fullscreen_button)
        #     if self._unfullscreen_button.get_parent() == self._stage:
        #         self._stage.remove_child(self._unfullscreen_button)

    def set_presenter(self, presenter):
        self._presenter = presenter
