import tempfile
import collections

import Image
import ImageOps
import ImageFilter

from gi.repository import Gtk

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
        self._src_image = None
        self._curr_image = None
        self._is_saved = True
        self._build_filter_dict()

    def _build_filter_dict(self):
        self._filter_dict = collections.OrderedDict([
            (_("NORMAL"), lambda im: im),
            (_("GRAYSCALE"), lambda im: ImageTools.grayscale(im)),
            (_("COUNTRY"), lambda im: ImageTools.country(im)),
            (_("GRUNGIFY"), lambda im: ImageTools.grunge(im)),
            (_("OLD PHOTO"), lambda im: ImageTools.old_photo(im)),
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

    def open(self, filename):
        self._filename = filename
        self._src_image = ImageTools.limit_size(Image.open(filename), (2056, 2056))
        self._curr_image = self._src_image
        self._curr_filter = self.get_default_filter_name()
        self._is_saved = True

    def save(self, filename, format=None):
        if self._curr_image is not None:
            if format is not None:
                self._curr_image.save(filename, format)
            else:
                self._curr_image.save(filename)
            self._is_saved = True

    def save_to_tempfile(self):
        filename = ""
        if ImageTools.has_alpha(self._curr_image):
            filename = tempfile.mkstemp('.png')[1]
            self._curr_image.save(filename)
        else:
            filename = tempfile.mkstemp('.jpg')[1]
            self._curr_image.save(filename, quality=95)
        return filename

    def is_open(self):
        return self._curr_image is not None

    def is_saved(self):
        return self._is_saved

    def is_modified(self):
        return self._curr_filter is not self.get_defualt_filter_name()

    def get_curr_filename(self):
        if not self.is_open():
            return None
        return self._filename

    def get_image(self):
        return self._curr_image

    def get_filter_names(self):
        return self._filter_dict.keys()

    def get_filter_names_and_thumbnails(self):
        names_and_thumbs = []
        filter_no = 0
        for name in self._filter_dict.keys():
            names_and_thumbs.append((name, "filter_" + str(filter_no) + ".jpg"))
            filter_no += 1
        return names_and_thumbs

    def get_default_filter_name(self):
        return self._filter_dict.keys()[0]

    def apply_filter(self, filter_name):
        if (not self.is_open()) or self._curr_filter == filter_name:
            return
        self._curr_filter = filter_name
        self._is_saved = False
        if filter_name in self._filter_dict:
            self._curr_image = self._filter_dict[filter_name](self._src_image)
        else:
            self._is_saved = True
            print "Filter not supported!"
