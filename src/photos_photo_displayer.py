from gi.repository import Gtk, GdkPixbuf

class PhotoDisplayer(Gtk.Image):
    """
    Sizes the image to fit centered in the space allotted.
    """
    
    # Constants
    MIN_SIZE = 100

    def __init__(self, **kw):
        super(PhotoDisplayer, self).__init__(name="photo-image", **kw)
        self._width = 0
        self._height = 0
        self._ascpect = 1
        self._pixbuf = None
        # self.load_from_file("../images/Background_Texture-Light.jpg")
        self.connect("size-allocate", self.resize_callback)

    def load_from_file(self, file):
        self._pixbuf = GdkPixbuf.Pixbuf.new_from_file(file)
        self._width = self._pixbuf.get_width()
        self._height = self._pixbuf.get_height()
        self._ascpect = self._width / float(self._height)
        self.queue_resize()

    def do_get_request_mode(self):
        return Gtk.SizeRequestMode.CONSTANT_SIZE
    
    def do_get_preferred_width(self):
        return PhotoDisplayer.MIN_SIZE, max(PhotoDisplayer.MIN_SIZE, self._width)

    def do_get_preferred_height(self):
        return PhotoDisplayer.MIN_SIZE, max(PhotoDisplayer.MIN_SIZE, self._height)

    # def do_get_preferred_width_for_height(self, height):
    #     print self._ascpect
    #     return height * self._ascpect, height * self._ascpect

    # def do_get_preferred_height_for_width(self, width):
    #     print self._ascpect, width
    #     ret = width / self._ascpect, width / self._ascpect
    #     print ret
    #     return width / self._ascpect, width / self._ascpect

    def resize_callback(self, w, alloc):
        if self._pixbuf == None: return
        border = self.get_style_context().get_border(Gtk.StateFlags.NORMAL)
        border_size = max(border.top, border.bottom, border.left, border.right)
        final_width = min(alloc.width - 2 * border_size, self._width)
        final_height = min(alloc.height - 2 * border_size, self._height)
        if (alloc.width / float(alloc.height)) > self._ascpect:
            final_width = final_height * self._ascpect
        else:
            final_height = final_width / self._ascpect
        self._sized_pixbuf = self._pixbuf.scale_simple(final_width, final_height, GdkPixbuf.InterpType.BILINEAR)
        self.set_from_pixbuf(self._sized_pixbuf)
