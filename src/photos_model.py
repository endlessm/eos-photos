import os
import tempfile
import numpy
import Image
import ImageOps
import ImageFilter
import collections

from filter import Filter
from filter import FilterManager

class PhotosModel(object):
    """
    The model for the photo being edited. Uses the Python Imaging Library to
    modify the current open photo.
    """

    def __init__(self, textures_path="", curves_path=""):
        super(PhotosModel, self).__init__()
        self._src_image = None
        self._curr_image = None
        self._is_saved = True
        self._textures_path = textures_path
        self._curves_path = curves_path
        self._build_filter_dict()

    def _build_filter_dict(self):
        self._filter_dict = collections.OrderedDict([
            (_("NORMAL"), lambda im: im),
            (_("GRAYSCALE"), lambda im: ImageOps.grayscale(im)),
            (_("SEPIA"), lambda im: self.apply_palette(im, self.make_linear_ramp((255, 201, 159)))),
            (_("PIXELATE"), lambda im: self.pixelate(im)),
            (_("BOXELATE"), lambda im: self.boxelate(im)),
            (_("OLD PHOTO"), lambda im: self.old_photo(im)),
            (_("GRUNGIFY"), lambda im: self.texture_overlay(im, self._textures_path + "grunge.jpg", 0.15)),
            (_("SCRATCH"), lambda im: self.texture_overlay(im, self._textures_path + "old_film.jpg", 0.25)),
            (_("FABRIC"), lambda im: self.texture_overlay(im, self._textures_path + "fabric.jpg", 0.35)),
            (_("BUMPY"), lambda im: self.texture_overlay(im, self._textures_path + "bumpy.jpg", 0.35)),
            (_("PAPER"), lambda im: self.texture_overlay(im, self._textures_path + "paper.jpg", 0.35)),
            (_("CONTOUR"), lambda im: im.filter(ImageFilter.CONTOUR)),
            (_("SMOOTH"), lambda im: im.filter(ImageFilter.SMOOTH_MORE)),
            (_("SHARPEN"), lambda im: im.filter(ImageFilter.SHARPEN)),
            (_("EMBOSS"), lambda im: im.filter(ImageFilter.EMBOSS)),
            (_("EDGES"), lambda im: im.filter(ImageFilter.FIND_EDGES)),
            (_("BLUR"), lambda im: im.filter(ImageFilter.BLUR)),
            (_("INVERT"), lambda im: self.invert(im)),
            (_("SOLARIZE"), lambda im: self.solarize(im)),
            (_("POSTERIZE"), lambda im: self.posterize(im)),
            (_("COUNTRY"), lambda im: self._apply_filter_ext(im, "country.acv")),
            (_("CROSS PROCESS"), lambda im: self._apply_filter_ext(im, "crossprocess.acv")),
            (_("DESERT"), lambda im: self._apply_filter_ext(im, "desert.acv")),
            (_("FOGGY BLUE"), lambda im: self._apply_filter_ext(im, "fogy_blue.acv")),
            (_("FRESH BLUE"), lambda im: self._apply_filter_ext(im, "fresh_blue.acv")),
            (_("LUMO"), lambda im: self._apply_filter_ext(im, "lumo.acv")),
            (_("NASHVILLE"), lambda im: self._apply_filter_ext(im, "nashville.acv")),
            (_("YELLOW BLUE"), lambda im: self._apply_filter_ext(im, "new_2_fresh_blue.acv")),
            (_("PORTRAESQUE"), lambda im: self._apply_filter_ext(im, "portraesque.acv")),
            (_("PROVIAESQUE"), lambda im: self._apply_filter_ext(im, "proviaesque.acv")),
            (_("VELVIAESQUE"), lambda im: self._apply_filter_ext(im, "velviaesque.acv")),
            (_("TRAINS"), lambda im: self._apply_filter_ext(im, "trains.acv")),
        ])

    def open(self, filename):
        self._filename = filename
        self._src_image = self.limit_size(Image.open(filename), (2056, 2056))
        self._curr_image = self._src_image
        self._curr_filter = self.get_default_name()
        self._is_saved = True
        

    def save(self, filename, format=None):
        if self._curr_image != None:
            if format!=None:
                self._curr_image.save(filename, format)
            else: self._curr_image.save(filename)
            self._is_saved = True

    def get_image(self):
        return self._curr_image

    def is_open(self):
        return self._curr_image != None

    def get_curr_filename(self):
        if not self.is_open(): return None
        return self._filename

    def is_saved(self):
        return self._is_saved

    def is_modified(self):
        return self._curr_filter is not "NORMAL"

    def get_filter_names(self):
        return self._filter_dict.keys()

    def get_default_name(self):
        return "NORMAL"

    def save_to_tempfile(self):
        filename = ""
        if self.has_alpha(self._curr_image):
            filename = tempfile.mkstemp('.png')[1]
            self._curr_image.save(filename)
        else:
            filename = tempfile.mkstemp('.jpg')[1]
            self._curr_image.save(filename, quality=95)
        return filename

    def _apply_filter_ext(self, image, filter_file):
        img_filter = Filter(self._curves_path + filter_file, 'crgb')
        
        image_array = numpy.array(image)

        filter_manager = FilterManager()
        filter_manager.add_filter(img_filter)

        filter_array = filter_manager.apply_filter('crgb', image_array)
        return Image.fromarray(filter_array)


    def apply_filter(self, filter_name):
        if (not self.is_open()) or self._curr_filter == filter_name: return
        self._curr_filter = filter_name
        self._is_saved = False
        if filter_name in self._filter_dict:
            self._curr_image = self._filter_dict[filter_name](self._src_image)
        else:
            self._is_saved = True
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

    def pixelate(self, image, pixel_size=10):
        width, height = image.size
        downsized = image.resize((width/16, height/16))
        return downsized.resize((width, height))

    def texture_overlay(self, image, texture_path, alpha=0.5):
        texture = Image.open(texture_path)
        texture = texture.resize(image.size)
        texture = texture.convert(image.mode)
        return Image.blend(image, texture, alpha)

    def has_alpha(self, image):
        return 'a' in image.mode.lower()

    def kill_alpha(self, image):
        if self.has_alpha(image):
            return image.convert("RGB")
        return image

    def old_photo(self, image):
        image = self._apply_filter_ext(image, "lumo.acv")
        image = self.apply_palette(image, self.make_linear_ramp((255, 201, 159)))
        return self.texture_overlay(image, self._textures_path + "old_film.jpg", 0.25)

    # These filters don't support an alpha channel, so we have to loose all transparencies.
    def boxelate(self, image):
        image = self.kill_alpha(image)
        image = self.pixelate(image)
        return image.filter(ImageFilter.FIND_EDGES)

    def invert(self, image):
        image = self.kill_alpha(image)
        return ImageOps.invert(image)

    def solarize(self, image):
        image = self.kill_alpha(image)
        return ImageOps.solarize(image)

    def posterize(self, image, bits=2):
        image = self.kill_alpha(image)
        return ImageOps.posterize(image, bits)
