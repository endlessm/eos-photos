from gi.repository import Gtk, GdkPixbuf, GtkClutter, Clutter

from widgets.clutter_image_button import ClutterImageButton

class ImageViewer(Gtk.Alignment):
    """
    Sizes the image to fit centered in the space allotted.
    """

    # Constants
    MIN_SIZE = 100
    PHOTO_HORIZ_PADDING = 10
    PHOTO_VERT_PADDING = 30
    BORDER_WIDTH = 7
    BORDER_COLOR = '#fff'

    def __init__(self, images_path="", **kw):
        super(ImageViewer, self).__init__(xalign=0.5, yalign=0.5, xscale=0.0, yscale=0.0, **kw)
        self._embed = GtkClutter.Embed.new()
        self._embed.connect('size-allocate', self._on_embed_size_allocate)
        self._stage = self._embed.get_stage()
        
        self._border = Clutter.Actor()
        color = Clutter.Color.new(0, 0, 0, 255)
        color.from_string(self.BORDER_COLOR)
        self._border.set_background_color(color)
        self._border.add_constraint(Clutter.AlignConstraint(
            align_axis=Clutter.AlignAxis.BOTH, factor=0.5, source=self._stage))
        self._stage.add_child(self._border)

        self._image_back = Clutter.Texture.new_from_file(images_path + "transparent_tile.png")
        self._image_back.set_repeat(True, True)
        self._image_back.add_constraint(Clutter.AlignConstraint(
            align_axis=Clutter.AlignAxis.BOTH, factor=0.5, source=self._stage))
        self._stage.add_child(self._image_back)
        
        self._image = Clutter.Texture()
        self._image.add_constraint(Clutter.AlignConstraint(
            align_axis=Clutter.AlignAxis.BOTH, factor=0.5, source=self._stage))
        self._stage.add_child(self._image)

        self._fullscreen_button = ClutterImageButton(normal_path=images_path + "expand-image_normal.png",
                                                 hover_path=images_path + "expand-image_hover.png",
                                                 down_path=images_path + "expand-image_down.png",
                                                 name="fullscreen-button")
        self._fullscreen_button.set_margin_bottom(ImageViewer.BORDER_WIDTH)
        self._fullscreen_button.set_margin_right(ImageViewer.BORDER_WIDTH)
        self._fullscreen_button.add_constraint(Clutter.AlignConstraint(
            align_axis=Clutter.AlignAxis.BOTH, factor=1.0, source=self._stage))
        self._fullscreen_button.get_click_action().connect('clicked', lambda w, e: self._presenter.on_fullscreen())

        self._unfullscreen_button = ClutterImageButton(normal_path=images_path + "expand-image-close_normal.png",
                                                 hover_path=images_path + "expand-image-close_hover.png",
                                                 down_path=images_path + "expand-image-close_down.png",
                                                 name="fullscreen-button")
        self._unfullscreen_button.add_constraint(Clutter.AlignConstraint(
            align_axis=Clutter.AlignAxis.BOTH, factor=1.0, source=self._stage))
        self._unfullscreen_button.get_click_action().connect('clicked', lambda w, e: self._presenter.on_unfullscreen())
        
        self._image_natural_size = (0, 0)
        self._image_open = False
        self.set_fullscreen_mode(False)
        
        self.set_hexpand(True)
        self.set_vexpand(True)
        # self.connect('size-allocate', self._on_size_allocate)
        self.add(self._embed)
        self.show()

    def set_fullscreen_mode(self, fullscreen):
        self._fullscreen_mode = fullscreen
        if fullscreen:
            self.set_padding(padding_top=0, padding_bottom=0,
                             padding_left=0, padding_right=0)
            self._stage.add_child(self._unfullscreen_button)
            if self._fullscreen_button.get_parent() == self._stage:
                self._stage.remove_child(self._fullscreen_button)
        else:
            self.set_padding(padding_top=ImageViewer.PHOTO_VERT_PADDING,
                             padding_bottom=ImageViewer.PHOTO_VERT_PADDING,
                             padding_left=ImageViewer.PHOTO_HORIZ_PADDING,
                             padding_right=ImageViewer.PHOTO_HORIZ_PADDING)
            self._stage.add_child(self._fullscreen_button)
            if self._unfullscreen_button.get_parent() == self._stage:
                self._stage.remove_child(self._unfullscreen_button)
        self.queue_resize()

    def load_from_data(self, data, width, height):
        self._image_open = True
        self._image_natural_size = (width, height)
        self._image.set_from_rgb_data(data, True, width, height, 0, 4, 0)
        self._fit_image(self.get_allocation())
        self._embed.show_all()

    def set_presenter(self, presenter):
        self._presenter = presenter

    def _fit_image(self, allocation):
        width, height = self._image_natural_size
        available_width, available_height = self._get_available_space(allocation)
        if available_width < width or available_height < height:
            scale = min(available_height / float(height), available_width / float(width))
            height *= scale
            width *= scale
        self._set_image_onscreen_size((width, height))

    def _set_image_onscreen_size(self, size):
        width, height = size
        if not self._fullscreen_mode:
            width += ImageViewer.BORDER_WIDTH * 2
            height += ImageViewer.BORDER_WIDTH * 2
        self._embed.set_size_request(width, height)

    def _get_available_space(self, allocation):
        available_width = allocation.width
        available_height = allocation.height
        if not self._fullscreen_mode:
            available_width = allocation.width - (ImageViewer.BORDER_WIDTH + ImageViewer.PHOTO_HORIZ_PADDING) * 2
            available_height = allocation.height - (ImageViewer.BORDER_WIDTH + ImageViewer.PHOTO_VERT_PADDING) * 2
        return available_width, available_height

    def _on_embed_size_allocate(self, widget, allocation):
        image_width = allocation.width
        image_height = allocation.height
        if not self._fullscreen_mode:
            image_width = max(0, allocation.width - ImageViewer.BORDER_WIDTH * 2)
            image_height = max(0, allocation.height - ImageViewer.BORDER_WIDTH * 2)            
        self._image.set_size(image_width, image_height)
        self._image_back.set_size(image_width, image_height)
        self._border.set_size(allocation.width, allocation.width)

    # Overrides. This is a hacky way to keep our alignment from asking for too
    # much space if the image is too big.
    def do_size_allocate(self, allocation):
        if self._image_open: self._fit_image(allocation)
        Gtk.Alignment.do_size_allocate(self, allocation)

    def do_get_request_mode(self):
        return Gtk.SizeRequestMode.CONSTANT_SIZE

    def do_get_preferred_width(self):
        return ImageViewer.MIN_SIZE, ImageViewer.MIN_SIZE

    def do_get_preferred_height(self):
        return ImageViewer.MIN_SIZE, ImageViewer.MIN_SIZE
