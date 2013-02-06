import os
import tempfile
import array
from gi.repository import GdkPixbuf
import numpy

class PhotosPresenter(object):
    """
    Presenter class for the photo application. Interacts with view and model
    and handles the main logic of the application.
    """
    def __init__(self, model=None, view=None):
        self._model = model
        self._view = view
        self._view.set_presenter(self)
        filters = self._model.get_filter_names()
        self._view.set_filter_names(filters, self._model.get_default_name())

    def _update_view(self):
        im = self._model.get_image().convert('RGBA')
        width, height = im.size
        self._view.replace_image_from_data(im.tostring(),
                                           width, height)

    #UI callbacks...
    def on_close(self):
        # Prompt for save?
        self._view.close_window()

    def on_minimize(self):
        self._view.minimize_window()

    def on_open(self):
        filename = self._view.show_open_dialog()
        if filename != None:
            self._model.open(filename)
            self._view.select_filter(self._model.get_default_name())
            self._update_view()
            
    def on_save(self):
        if not self._model.is_open(): return
        filename = self._view.show_save_dialog()
        if filename != None:
            self._model.save(filename)

    def on_share(self):
        print "Share called"

    def on_fullscreen(self):
        print "Fullscreen called"

    def on_filter_select(self, filter_name):
        if not self._model.is_open(): return
        self._model.apply_filter(filter_name)
        self._update_view()

    # def image_to_pixbuf(self, img):
    #     if img.mode != 'RGB':
    #         img = img.convert('RGB')
    #     buff = StringIO.StringIO()
    #     img.save(buff, 'ppm')
    #     contents = buff.getvalue()
    #     buff.close()
    #     loader = GdkPixbuf.PixbufLoader.new_with_type('pnm')
    #     loader.write(contents)
    #     pixbuf = loader.get_pixbuf()
    #     loader.close()
    #     return pixbuf
