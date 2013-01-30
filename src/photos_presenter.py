import os
from gi.repository import Gtk, GdkPixbuf, Gdk
import Image
import StringIO

class PhotosPresenter(object):
    def __init__(self, model=None, view=None):
        self._model = model
        self._view = view
        self._view.set_presenter(self)

    def close(self):
        # Prompt for save?
        self._view.close_window()

    def minimize(self):
        self._view.minimize_window()

    def open(self):
        print "Open called"
        TEMP_FILE = os.path.expanduser("~/Desktop/temp.jpg")
        
        # Opens a dialog window where the user can choose an image file
        dialog = Gtk.FileChooserDialog ("Open Image", None, Gtk.FileChooserAction.OPEN);

        # Adds 'Cancel' and 'Open' buttons
        dialog.add_button (Gtk.STOCK_CANCEL, 0)
        dialog.add_button (Gtk.STOCK_OK, 1)

        # Sets deafault to 'Open'
        dialog.set_default_response(1)

        # Filters and displays files which can be opened by Gtk.Image
        filefilter = Gtk.FileFilter ()
        filefilter.add_pixbuf_formats ()
        dialog.set_filter(filefilter)

        if dialog.run() == 1:

            # Loads the image
            FILE_NAME = dialog.get_filename()
            new_image = Gtk.Image(file=FILE_NAME, name="photo-image")
            #im = Image.open(FILE_NAME)

            # Creates a thumbnail of the given size
            # size = 50, 50
            # im.thumbnail(size, Image.ANTIALIAS)
            #im.save(TEMP_FILE)

            # Converts image to pixbuf
            #pbuf = self.image_to_pixbuf(im)
            self._view.replace_image(new_image)
            # Displays the chosen image
            #self.image.set_from_pixbuf(pbuf)

        dialog.destroy()


    def image_to_pixbuf(self, img):
        if img.mode != 'RGB':
            img = img.convert('RGB')
        buff = StringIO.StringIO()
        img.save(buff, 'ppm')
        contents = buff.getvalue()
        buff.close()
        loader = GdkPixbuf.PixbufLoader.new_with_type('pnm')
        loader.write(contents)
        pixbuf = loader.get_pixbuf()
        loader.close()
        return pixbuf

    def save(self):
        print "Save called"

    def share(self):
        print "Share called"

