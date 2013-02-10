import os
import Image
import ImageOps
import ImageFilter

from filter import Filter
from filter import FilterManager
import numpy


class PhotosModel(object):
    """
    The model for the photo being edited. Uses the Python Imaging Library to
    modify the current open photo.
    """
    def __init__(self):
        super(PhotosModel, self).__init__()
        self._src_image = None
        self._curr_image = None

    def open(self, filename):
        self._filename = filename
        self._src_image = self.limit_size(Image.open(filename), (2056, 2056))
        self._curr_image = self._src_image
        self._curr_filter = self.get_default_name()

    def save(self, filename, format=None):
        if self._curr_image != None:
            if format!=None:
                self._curr_image.save(filename, format)
            else: self._curr_image.save(filename)    

    def get_image(self):
        return self._curr_image

    def is_open(self):
        return self._curr_image != None

    def get_curr_filename(self):
        if not self.is_open(): return None
        return self._filename

    def is_modified(self):
        return self._curr_filter == "NORMAL"

    def get_filter_names(self):
        return ["NORMAL", "GRAYSCALE", "SEPIA", "PIXELATE", 
        "CONTOUR", "SMOOTH", "SHARPEN", "EMBOSS", "INVERT", 
        "SOLARIZE", "FIND_EDGES", "BLUR", "COUNTRY", "DESERT", 
        "NASHVILLE", "CROSSPROCESS", "LUMO", "PORTRAESQUE", 
        "VELVIAESQUE", "PROVIAESQUE"]

    def get_default_name(self):
        return "NORMAL"

    def _apply_filter_ext(self, filter_name):
        img_filter = Filter("../data/curves/" + filter_name.lower() + ".acv", 'crgb')
        
        image_array = numpy.array(self._src_image)

        filter_manager = FilterManager()
        filter_manager.add_filter(img_filter)

        filter_array = filter_manager.apply_filter('crgb', image_array)
        self._curr_image = Image.fromarray(filter_array)


    def apply_filter(self, filter_name):
        if (not self.is_open()) or self._curr_filter == filter_name: return
        self._curr_filter = filter_name
        if filter_name == "NORMAL":
            self._curr_image = self._src_image.copy()
        elif filter_name == "GRAYSCALE":
            self._curr_image = ImageOps.grayscale(self._src_image)
        elif filter_name == "SEPIA":
            self._curr_image = self.apply_palette(self._src_image, self.make_linear_ramp((255, 201, 159)))
        elif filter_name == "PIXELATE":
            self._curr_image = self.pixelate(self._src_image, 10)
        elif filter_name == "CONTOUR":
            self._curr_image = self._src_image.filter(ImageFilter.CONTOUR)
        elif filter_name == "SMOOTH":
            self._curr_image = self._src_image.filter(ImageFilter.SMOOTH_MORE)
        elif filter_name == "SHARPEN":
            self._curr_image = self._src_image.filter(ImageFilter.SHARPEN)
        elif filter_name == "EMBOSS":
            self._curr_image = self._src_image.filter(ImageFilter.EMBOSS)
        elif filter_name == "INVERT":
            self._curr_image = self.invert(self._src_image)
        elif filter_name == "SOLARIZE":
            self._curr_image = self.solarize(self._src_image)
        elif filter_name == "FIND_EDGES":
            self._curr_image = self._src_image.filter(ImageFilter.FIND_EDGES)
        elif filter_name == "BLUR":
            self._curr_image = self._src_image.filter(ImageFilter.BLUR)
        elif filter_name == "COUNTRY":
            self._apply_filter_ext(filter_name)
        elif filter_name == "DESERT":
            self._apply_filter_ext(filter_name)
        elif filter_name == "NASHVILLE":
            self._apply_filter_ext(filter_name)
        elif filter_name == "CROSSPROCESS":
            self._apply_filter_ext(filter_name)
        elif filter_name == "LUMO":
            self._apply_filter_ext(filter_name)
        elif filter_name == "PORTRAESQUE":
            self._apply_filter_ext(filter_name)
        elif filter_name == "VELVIAESQUE":
            self._apply_filter_ext(filter_name)
        elif filter_name == "PROVIAESQUE":
            self._apply_filter_ext(filter_name)
        else:
            print "Filter not supported!"

    def limit_size(self, image, size_limits):
        width, height = image.size
        width_limit, height_limit = size_limits
        if width < width_limit and height < height_limit:
            return image
        else:
            scale = min(width_limit / float(width), height_limit / float(height))
            new_size = map(int, (width * scale, height * scale))
            return image.resize(new_size, Image.BILINEAR)

    def grayscale(self, image):
        mode = image.mode
        image = ImageOps.grayscale(image)
        image = image.convert(mode)
        return image

    def make_linear_ramp(self, color):
        ramp = []
        r, g, b = color
        for i in range(256):
            ramp.extend((r*i/255, g*i/255, b*i/255))
        return ramp

    def apply_palette(self, image, palette):
        mode = image.mode
        image = image.convert("L")
        image.putpalette(palette)
        image = image.convert(mode)
        return image

    def pixelate(self, image, pixel_size):
        width, height = image.size
        downsized = image.resize((width/16, height/16))
        return downsized.resize((width, height))

    def invert(self, image):
        mode = image.mode
        if mode != "L" or "RGB":
            image = image.convert("RGB")
            image = ImageOps.invert(image)
            return image.convert(mode)
        else:
            return ImageOps.invert(image)

    def solarize(self, image):
        mode = image.mode
        if mode != "L" or "RGB":
            image = image.convert("RGB")
            image = ImageOps.solarize(image)
            return image.convert(mode)
        else:
            return ImageOps.invert(image)
