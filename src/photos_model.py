import os
import Image
import ImageOps
import ImageFilter

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
        self._src_image = Image.open(filename)
        self._curr_image = self._src_image
        self._curr_filter = self.get_default_name()

    def save(self, filename):
        if self._curr_image != None:
            self._curr_image.save(filename)

    def is_open(self):
        return self._curr_image != None

    def get_curr_filename(self):
        if not self.is_open(): return None
        return self._filename

    def is_modified(self):
        return self._curr_filter == "NORMAL"

    def get_filter_names(self):
        return ["NORMAL", "GRAYSCALE", "CONTOUR", "SMOOTH", "SHARPEN", "EMBOSS", "INVERT", "SOLARIZE", "FIND_EDGES", "BLUR"]

    def get_default_name(self):
        return "NORMAL"

    def apply_filter(self, filter_name):
        if (not self.is_open()) or self._curr_filter == filter_name: return
        self._curr_filter = filter_name
        if filter_name == "NORMAL":
            self._curr_image = self._src_image.copy()
        elif filter_name == "GRAYSCALE":
            self._curr_image = ImageOps.grayscale(self._src_image)
        elif filter_name == "CONTOUR":
            self._curr_image = self._src_image.filter(ImageFilter.CONTOUR)
        elif filter_name == "SMOOTH":
            self._curr_image = self._src_image.filter(ImageFilter.SMOOTH_MORE)
        elif filter_name == "SHARPEN":
            self._curr_image = self._src_image.filter(ImageFilter.SHARPEN)
        elif filter_name == "EMBOSS":
            self._curr_image = self._src_image.filter(ImageFilter.EMBOSS)
        elif filter_name == "INVERT":
            self._curr_image = ImageOps.invert(self._src_image)
        elif filter_name == "SOLARIZE":
            self._curr_image = ImageOps.solarize(self._src_image)
        elif filter_name == "FIND_EDGES":
            self._curr_image = self._src_image.filter(ImageFilter.FIND_EDGES)
        elif filter_name == "BLUR":
            self._curr_image = self._src_image.filter(ImageFilter.BLUR)
        else:
            print "Filter not supported!"