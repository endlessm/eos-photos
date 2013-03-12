import tempfile
import collections

import Image
import ImageOps
import ImageFilter

import image_processing.image_tools as ImageTools


class PhotosModel(object):
    """
    The model for the photo being edited. Uses the Python Imaging Library to
    modify the current open photo.
    """

    def __init__(self, textures_path="", curves_path=""):
        super(PhotosModel, self).__init__()
        ImageTools.set_textures_path(textures_path)
        ImageTools.set_curves_path(curves_path)
        self._source_image = None
        self._filtered_image = None
        self._adjusted_image = None

        self._is_saved = True
        self._build_filter_dict()
        self.reset_options()

    def _build_filter_dict(self):
        self._filter_dict = collections.OrderedDict([
            (_("NORMAL"), lambda im: im),
            (_("GRAYSCALE"), lambda im: ImageOps.grayscale(im)),
            (_("SEPIA"), lambda im: ImageTools.sepia_tone(im)),
            (_("PIXELATE"), lambda im: ImageTools.pixelate(im)),
            (_("BOXELATE"), lambda im: ImageTools.boxelate(im)),
            (_("OLD PHOTO"), lambda im: ImageTools.old_photo(im)),
            (_("GRUNGIFY"), lambda im: ImageTools.texture_overlay(im, "grunge.jpg", 0.15)),
            (_("SCRATCH"), lambda im: ImageTools.texture_overlay(im, "old_film.jpg", 0.25)),
            (_("FABRIC"), lambda im: ImageTools.texture_overlay(im, "fabric.jpg", 0.35)),
            (_("BUMPY"), lambda im: ImageTools.texture_overlay(im, "bumpy.jpg", 0.35)),
            (_("PAPER"), lambda im: ImageTools.texture_overlay(im, "paper.jpg", 0.35)),
            (_("CONTOUR"), lambda im: im.filter(ImageFilter.CONTOUR)),
            (_("SMOOTH"), lambda im: im.filter(ImageFilter.SMOOTH_MORE)),
            (_("SHARPEN"), lambda im: im.filter(ImageFilter.SHARPEN)),
            (_("EMBOSS"), lambda im: im.filter(ImageFilter.EMBOSS)),
            (_("EDGES"), lambda im: im.filter(ImageFilter.FIND_EDGES)),
            (_("BLUR"), lambda im: im.filter(ImageFilter.BLUR)),
            (_("INVERT"), lambda im: ImageTools.invert(im)),
            (_("SOLARIZE"), lambda im: ImageTools.solarize(im)),
            (_("POSTERIZE"), lambda im: ImageTools.posterize(im)),
            (_("COUNTRY"), lambda im: ImageTools.apply_curve(im, "country.acv")),
            (_("CROSS PROCESS"), lambda im: ImageTools.apply_curve(im, "crossprocess.acv")),
            (_("DESERT"), lambda im: ImageTools.apply_curve(im, "desert.acv")),
            (_("FOGGY BLUE"), lambda im: ImageTools.apply_curve(im, "fogy_blue.acv")),
            (_("FRESH BLUE"), lambda im: ImageTools.apply_curve(im, "fresh_blue.acv")),
            (_("LUMO"), lambda im: ImageTools.apply_curve(im, "lumo.acv")),
            (_("NASHVILLE"), lambda im: ImageTools.apply_curve(im, "nashville.acv")),
            (_("YELLOW BLUE"), lambda im: ImageTools.apply_curve(im, "new_2_fresh_blue.acv")),
            (_("PORTRAESQUE"), lambda im: ImageTools.apply_curve(im, "portraesque.acv")),
            (_("PROVIAESQUE"), lambda im: ImageTools.apply_curve(im, "proviaesque.acv")),
            (_("VELVIAESQUE"), lambda im: ImageTools.apply_curve(im, "velviaesque.acv")),
            (_("TRAINS"), lambda im: ImageTools.apply_curve(im, "trains.acv")),
        ])

    def reset_options(self):
        self._last_filter = self._filter = self._get_default_filter()
        self._last_brightness = self._brightness = 1.0
        self._last_contrast = self._contrast = 1.0
        self._last_saturation = self._saturation = 1.0

    def _get_default_filter(self):
        return self._filter_dict.keys()[0]

    def open(self, filename):
        self._filename = filename
        self._source_image = ImageTools.limit_size(Image.open(filename), (2056, 2056))
        self._adjusted_image = self._filtered_image = self._source_image
        self._is_saved = True

    def save(self, filename, format=None):
        if self.is_open() is not None:
            if format is not None:
                self.get_image().save(filename, format)
            else:
                self.get_image().save(filename)
            self._is_saved = True

    def save_to_tempfile(self):
        filename = ""
        if ImageTools.has_alpha(self.get_image()):
            filename = tempfile.mkstemp('.png')[1]
            self.get_image().save(filename)
        else:
            filename = tempfile.mkstemp('.jpg')[1]
            self.get_image().save(filename, quality=95)
        return filename

    def is_open(self):
        return self._source_image is not None

    def is_saved(self):
        return self._is_saved

    def is_modified(self):
        return self._curr_filter is not self.get_defualt_filter_name()

    def get_curr_filename(self):
        if not self.is_open():
            return None
        return self._filename

    def get_image(self):
        return self._adjusted_image

    def get_filter_names(self):
        return self._filter_dict.keys()

    def get_filter_names_and_thumbnails(self):
        names_and_thumbs = []
        filter_no = 0
        for name in self._filter_dict.keys():
            names_and_thumbs.append((name, "filter_" + str(filter_no) + ".jpg"))
            filter_no += 1
        return names_and_thumbs

    def get_contrast(self):
        return self._contrast

    def set_contrast(self, value):
        self._contrast = value
        self._update_image()

    def get_brightness(self):
        return self._brightness

    def set_brightness(self, value):
        self._brightness = value
        self._update_image()

    def get_saturation(self):
        return self._saturation

    def set_saturation(self, value):
        self._saturation = value
        self._update_image()

    def get_filter(self):
        return self._filter

    def set_filter(self, filter_name):
        self._filter = filter_name
        self._update_image()

    def _update_image(self):
        if (not self.is_open()):
            return
        filtered = False
        if not self._filter == self._last_filter:
            if self._filter in self._filter_dict:
                filtered = True
                self._last_filter = self._filter
                self._filtered_image = self._filter_dict[self._filter](self._source_image)
            else:
                print "Filter not supported!"
        adjusted = not (self._last_brightness == self._brightness
                        and self._last_contrast == self._contrast
                        and self._last_saturation == self._saturation)
        if filtered or adjusted:
            self._adjust_image()
            self._is_saved = False

    def _adjust_image(self):
        im = ImageTools.apply_contrast(self._filtered_image, self._contrast)
        im = ImageTools.apply_brightness(im, self._brightness)
        im = ImageTools.apply_saturation(im, self._saturation)
        self._adjusted_image = im
