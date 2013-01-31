from gi.repository import Gtk

from photos_top_toolbar import PhotosTopToolbar
from photos_left_toolbar import PhotosLeftToolbar
from photos_right_toolbar import PhotosRightToolbar
from photos_window import PhotosWindow

class PhotosView(object):
    """
    The main view class for the photo application. Mainly just passes the
    presenter calls to the appropriate UI elements. PhotosWindow does the
    actual toplevel layout of the toolbars and central view.
    """
    def __init__(self):
        self._top_toolbar = PhotosTopToolbar()
        self._left_toolbar = PhotosLeftToolbar()
        self._right_toolbar = PhotosRightToolbar()
        self._image = Gtk.Image(file="../images/test_photo.jpg", name="photo-image")
        self._window = PhotosWindow(self._top_toolbar, self._left_toolbar, self._right_toolbar, self._image)

    def set_presenter(self, presenter):
        self._presenter = presenter
        self._top_toolbar.set_presenter(presenter)
        self._left_toolbar.set_presenter(presenter)
        self._right_toolbar.set_presenter(presenter)

    def present_dialog(self):
        
        
        # Opens a dialog window where the user can choose an image file
        dialog = Gtk.FileChooserDialog ("Open Image", None, Gtk.FileChooserAction.OPEN);

        # Adds 'Cancel' and 'Open' buttons
        dialog.add_button (Gtk.STOCK_CANCEL, 0)
        dialog.add_button (Gtk.STOCK_OK, 1)

        # Sets default to 'Open'
        dialog.set_default_response(1)

        # Filters and displays files which can be opened by Gtk.Image
        filefilter = Gtk.FileFilter ()
        filefilter.add_pixbuf_formats ()
        dialog.set_filter(filefilter)

        if dialog.run() == 1:

            # Loads the image
            
            filename = dialog.get_filename()
            dialog.destroy()
            return filename
          

            #new_image = Gtk.Image(file=FILE_NAME, name="photo-image")
            #im = Image.open(FILE_NAME)

            # Creates a thumbnail of the given size
            # size = 50, 50
            # im.thumbnail(size, Image.ANTIALIAS)
            #im.save(TEMP_FILE)

            # Converts image to pixbuf
            #pbuf = self.image_to_pixbuf(im)
            
            # Displays the chosen image
            #self.image.set_from_pixbuf(pbuf)

        

    def get_window(self):
        return self._window

    def close_window(self):
        self._window.destroy()

    def minimize_window(self):
        self._window.iconify()

    def replace_image(self, image_name):
        image = Gtk.Image(file=image_name, name="photo-image")
        cur_image = self._window._image_align.get_children()[0]
        self._window._image_align.remove(cur_image)
        self._window._image_align.add(image)
        image.show()
        #self._window._image_align.get_children()[0].show()
