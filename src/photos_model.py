import os
import Image
class PhotosModel(object):
    """
    The model for the photo being edited. Uses the Python Imaging Library to
    modify the current open photo.
    """
    def __init__(self):
        super(PhotosModel, self).__init__()
        self._image = None
        self.TEMP_FILE = os.path.expanduser("~/Desktop/temp.jpg")


    def set_current_image(self, filename):
    	self._image = Image.open(filename)
    	self._image.save(self.TEMP_FILE)

    def get_current_image(self):
    	return self.TEMP_FILE

