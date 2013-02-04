import os
import tempfile

class PhotosPresenter(object):
    def __init__(self, model=None, view=None):
        self._model = model
        self._view = view
        self._view.set_presenter(self)
        filters = self._model.get_filter_names()
        self._view.set_filter_names(filters, self._model.get_default_name())

    def _update_view(self):
        temp_path = tempfile.mktemp(".png")
        self._model.save(temp_path)
        self._view.replace_image_from_file(temp_path)
        os.remove(temp_path)

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
        filename = self._view.show_save_dialog()
        if filename != None:
            self._model.save(filename)

    def on_share(self):
        print "Share called"

    def on_fullscreen(self):
        print "Fullscreen called"

    def on_filter_select(self, filter_name):
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
