import os
import Image
import ImageOps

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
        self._src_image = Image.open(filename)
        self._curr_image = self._src_image
        self._curr_filter = self.get_default_name()

    def save(self, filename):
        if self._curr_image != None:
            self._curr_image.save(filename)

    def get_filter_names(self):
        return ["NORMAL", "GRAYSCALE", "INVERT", "SOLARIZE", "TEST", "FOO", "BAR", "BINGO", "WHAAAA?"]

    def get_default_name(self):
        return "NORMAL"

    def apply_filter(self, filter_name):
        if self._curr_filter == filter_name: return
        self._curr_filter = filter_name
        if filter_name == "NORMAL":
            self._curr_image = self._src_image.copy()
        elif filter_name == "GRAYSCALE":
            self._curr_image = ImageOps.grayscale(self._src_image)
        elif filter_name == "INVERT":
            self._curr_image = ImageOps.invert(self._src_image)
        elif filter_name == "SOLARIZE":
            self._curr_image = ImageOps.solarize(self._src_image)
        else:
            print "Filter not supported!"