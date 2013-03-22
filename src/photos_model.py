import tempfile
import collections

import Image
import ImageFilter

import image_processing.image_tools as ImageTools


class PhotosModel(object):
    """
    The model for the photo being edited. Uses the Python Imaging Library to
    modify the current open photo.
    """
    def __init__(self, textures_path="", curves_path="", borders_path=""):
        super(PhotosModel, self).__init__()
        ImageTools.set_textures_path(textures_path)
        self._textures_path = textures_path
        ImageTools.set_curves_path(curves_path)
        self._curves_path = curves_path
        self._borders_path = borders_path
        self._source_image = None
        self._filtered_image = None
        self._adjusted_image = None

        self._is_saved = True
        self._build_filter_dict()
        self._build_border_dict()
        self._clear_options()

    def _build_filter_dict(self):
        self._filter_dict = collections.OrderedDict([
            (_("NORMAL"), lambda im: im),
            (_("GRAYSCALE"), lambda im: ImageTools.grayscale(im)),
            (_("COUNTRY"), lambda im: ImageTools.country(im)),
            (_("GRUNGIFY"), lambda im: ImageTools.grunge(im)),
            (_("OLD PHOTO"), lambda im: ImageTools.old_photo(im)),
            (_("COLORFUL"), lambda im: ImageTools.colorful(im)),
            # (_("BUMPY"), lambda im: ImageTools.bumpy(im)),
            (_("LUMO"), lambda im: ImageTools.lumo(im)),
            # (_("SMOOTH"), lambda im: im.filter(ImageFilter.SMOOTH_MORE)),
            # (_("SHARPEN"), lambda im: im.filter(ImageFilter.SHARPEN)),
            (_("FOGGY BLUE"), lambda im: ImageTools.foggy_blue(im)),
            (_("PAPER"), lambda im: ImageTools.paper(im)),
            (_("TRAINS"), lambda im: ImageTools.trains(im)),
            (_("DESERT"), lambda im: ImageTools.desert(im)),
            (_("POSTERIZE"), lambda im: ImageTools.posterize(im)),
            (_("INVERT"), lambda im: ImageTools.invert(im)),
            (_("EMBOSS"), lambda im: im.filter(ImageFilter.EMBOSS)),
            (_("EDGES"), lambda im: im.filter(ImageFilter.FIND_EDGES)),
            (_("PIXELATE"), lambda im: ImageTools.pixelate(im)),
            (_("BOXELATE"), lambda im: ImageTools.boxelate(im)),
        ])

    def _build_border_dict(self):
        self._border_dict = collections.OrderedDict([
            (_("NONE"), None),
            (_("HORIZONTAL BARS"), "horizontal_bars.png"),
            (_("SIDE BARS"), "vertical_bars.png"),
            (_("TEST"), "border-1.png"),
            (_("TEST2"), "border-2.png"),
            (_("TEST3"), "border-3.png"),
            (_("TEST4"), "border-4.png"),
            (_("TEST5"), "border-5.png")
        ])

    def _clear_options(self):
        self._last_filter = self._filter = self._get_default_filter()
        self._last_brightness = self._brightness = 1.0
        self._last_contrast = self._contrast = 1.0
        self._last_saturation = self._saturation = 1.0
        self._border = self._get_default_border()
        self._border_image = None

    def _get_default_filter(self):
        return self._filter_dict.keys()[0]

    def _get_default_border(self):
        return self._border_dict.keys()[0]

    def open(self, filename):
        self._filename = filename
        self._source_image = ImageTools.limit_size(Image.open(filename), (2056, 2056)).convert('RGB')
        self._adjusted_image = self._filtered_image = self._source_image
        self._is_saved = True
        self._clear_options()

    def save(self, filename, format=None):
        if self.is_open():
            im = self._composite_final_image()
            if format is not None:
                im.save(filename, format)
            else:
                im.save(filename)
            self._is_saved = True

    def save_to_tempfile(self):
        if self.is_open():
            filename = ""
            im = self._composite_final_image()
            # PNG would give no loss from current image, but a lot bigger.
            # Would take longer to upload to facebook/gmail.
            # filename = tempfile.mkstemp('.png')[1]
            # im.save(filename)
            filename = tempfile.mkstemp('.jpg')[1]
            im.save(filename, quality=95)
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

    def get_base_image(self):
        return self._adjusted_image

    def get_border_image(self):
        return self._border_image

    def get_filter_names(self):
        return self._filter_dict.keys()

    def get_filter_names_and_thumbnails(self):
        names_and_thumbs = []
        filter_no = 0
        for name in self._filter_dict.keys():
            names_and_thumbs.append((name, "filter_" + str(filter_no) + ".jpg"))
            filter_no += 1
        return names_and_thumbs

    def get_border_names_and_thumbnails(self):
        names_and_thumbs = []
        for name in self._border_dict.keys():
            names_and_thumbs.append((name, "Filters_Example-Picture_01.jpg"))
        return names_and_thumbs

    def get_contrast(self):
        return self._contrast

    def set_contrast(self, value):
        self._contrast = value
        self._update_base_image()

    def get_brightness(self):
        return self._brightness

    def set_brightness(self, value):
        self._brightness = value
        self._update_base_image()

    def get_saturation(self):
        return self._saturation

    def set_saturation(self, value):
        self._saturation = value
        self._update_base_image()

    def get_filter(self):
        return self._filter

    def set_filter(self, filter_name):
        self._filter = filter_name
        self._update_base_image()

    def get_border(self):
        return self._border

    def set_border(self, border_name):
        if (not self.is_open()):
            return
        self._border = border_name
        filename = self._border_dict[border_name]
        print filename
        if filename is not None:
            self._border_image = Image.open(self._borders_path + filename).resize(
                self._source_image.size, Image.BILINEAR)
        else:
            self._border_image = None

    def _update_base_image(self):
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
            self._adjust_base_image()
            self._is_saved = False

    def _adjust_base_image(self):
        im = ImageTools.apply_contrast(self._filtered_image, self._contrast)
        im = ImageTools.apply_brightness(im, self._brightness)
        im = ImageTools.apply_saturation(im, self._saturation)
        self._adjusted_image = im

    def _composite_final_image(self):
        return Image.composite(self.get_border_image(), self.get_base_image(), self.get_border_image())
