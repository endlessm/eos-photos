from gi.repository import Gtk, GdkPixbuf, GtkClutter, Clutter

from image_button import ImageButton

class ImageViewer(Gtk.Alignment):
    """
    Sizes the image to fit centered in the space allotted.
    """

    # Constants
    MIN_SIZE = 100
    PHOTO_HORIZ_PADDING = 10
    PHOTO_VERT_PADDING = 30
    # TODO: Read this from the css.
    BORDER_WIDTH = 7
    BORDER_COLOR = '#fff'

    def __init__(self, **kw):
        super(ImageViewer, self).__init__(xalign=0.5, yalign=0.5, xscale=0.0, yscale=0.0, **kw)
        self._embed = GtkClutter.Embed.new()
        self._embed.connect('size-allocate', self._on_embed_size_allocate)
        self._stage = self._embed.get_stage()
        self._image = Clutter.Texture.new()
        self._border = Clutter.Rectangle.new()
        self._border.set_border_width(ImageViewer.BORDER_WIDTH)
        color = Clutter.Color.new(0, 0, 0, 255)
        color.from_string(self.BORDER_COLOR)
        self._border.set_border_color(color)
        background = Clutter.Texture.new_from_file('../images/Background_Texture-Light.jpg')
        self._stage.add_child(background)
        self._stage.add_child(self._border)
        self._stage.add_child(self._image)

        self._fullscreen_button = ImageButton(normal_path="../images/expand-image_normal.png",
                                              hover_path="../images/expand-image_hover.png",
                                              down_path="../images/expand-image_down.png",
                                              name="close-button")
        self._fullscreen_button.set_halign(Gtk.Align.END)
        self._fullscreen_button.set_valign(Gtk.Align.END)
        self._fullscreen_button.set_margin_right(ImageViewer.BORDER_WIDTH)
        self._fullscreen_button.set_margin_bottom(ImageViewer.BORDER_WIDTH)
        self._fullscreen_button.connect('clicked', lambda w: self._presenter.on_fullscreen())
        
        self._overlay = Gtk.Overlay()
        self._overlay.add(embed)
        self._overlay.add_overlay(self._fullscreen_button)
        
        self.set_padding(padding_top=ImageViewer.PHOTO_VERT_PADDING,
                                      padding_bottom=ImageViewer.PHOTO_VERT_PADDING,
                                      padding_left=ImageViewer.PHOTO_HORIZ_PADDING,
                                      padding_right=ImageViewer.PHOTO_HORIZ_PADDING)
        self.add(self._overlay)
        self.show_all()

        # self.connect("size-allocate", self.resize_callback)

    def load_from_pixbuf(self, pixbuf):
        # TODO: this doesn't support resizing, and is pretty ugly code. Fix me up!
        alloc = self.get_allocation()
        max_width = alloc.width - 2 * ImageViewer.BORDER_WIDTH - 2 * ImageViewer.PHOTO_HORIZ_PADDING
        max_height = alloc.height - 2 * ImageViewer.BORDER_WIDTH - 2 * ImageViewer.PHOTO_VERT_PADDING
        width = pixbuf.get_width()
        height = pixbuf.get_height()
        if width > max_width or height > max_height:
            ascpect = width / float(height)
            final_width = min(width, max_width)
            final_height = min(height, max_height)
            if (alloc.width / float(alloc.height)) > ascpect:
                final_width = final_height * ascpect
            else:
                final_height = final_width / ascpect
            sized_pixbuf = pixbuf.scale_simple(final_width, final_height, GdkPixbuf.InterpType.BILINEAR)
            self._image.set_from_pixbuf(sized_pixbuf)
        else:
            self._image.set_from_pixbuf(pixbuf)
        self._overlay.show_all()

    def load_from_data(self, data, width, height):
        self._image.set_from_rgb_data(data, True, width, height, 0, 4, 0)
        allocation = self.get_allocation()
        available_width, available_height = allocation.width, allocation.height
        if available_width < width or available_height < height:
            if height < width:
                height = height * available_width / width
                width = available_width
            else:
                width = width * available_height / height
                height = available_height
        self._embed.set_size_request(width, height)

    def load_from_file(self, file):
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(file)
        self.load_from_pixbuf(pixbuf)

    def do_get_request_mode(self):
        return Gtk.SizeRequestMode.CONSTANT_SIZE

    def do_get_preferred_width(self):
        return ImageViewer.MIN_SIZE, 9999999

    def do_get_preferred_height(self):
        return ImageViewer.MIN_SIZE, 9999999

    def set_presenter(self, presenter):
        self._presenter = presenter

    def _on_embed_size_allocate(self, widget, allocation):
        self._image.set_size(allocation.width - ImageViewer.BORDER_WIDTH * 2,
                             allocation.height - ImageViewer.BORDER_WIDTH * 2)
        self._border.set_size(allocation.width, allocation.height)

        self._border.set_anchor_point(allocation.width / 2,
                                      allocation.height / 2)
        self._border.set_position(allocation.width / 2,
                                  allocation.height / 2)
        width, height = self._image.get_size()
        self._image.set_anchor_point(width / 2, height / 2)
        self._image.set_position(allocation.width / 2,
                                 allocation.height / 2)
