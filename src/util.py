import Image
import io
from gi.repository import Clutter, Cogl, GdkPixbuf, Gio

def load_clutter_image_from_resource(resource_path):
    pixbuf = GdkPixbuf.Pixbuf.new_from_resource(resource_path)
    image = Clutter.Image()
    if pixbuf is not None:
        format = Cogl.PixelFormat.RGB_888
        if pixbuf.get_has_alpha():
            format = Cogl.PixelFormat.RGBA_8888
        image.set_data(pixbuf.get_pixels(),
                       format,
                       pixbuf.get_width(),
                       pixbuf.get_height(),
                       pixbuf.get_rowstride())
    return image

def load_byte_stream_from_resource(resource_path):
    gbytes = Gio.resources_lookup_data(resource_path, Gio.ResourceFlags.NONE)
    return io.BytesIO(gbytes.get_data())

def load_pil_image_from_resource(resource_path):
    return Image.open(load_byte_stream_from_resource(resource_path))
