import os
import tempfile
import array

VALID_FILE_TYPES = ["jpg", "png", "gif"]

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

    def _check_extension(self, filename, original_ext):
        name_arr = filename.split(".")
        ext = name_arr.pop(-1)

        if not name_arr:
            # there was no extension
            name_arr = [filename]
            ext = ""
        dot_join = "."

        # If extension is not a valid file type we use the extension of the original file
        if ext not in VALID_FILE_TYPES:
            return dot_join.join(name_arr) + "." + original_ext
        return filename
            
    def on_save(self):
        if not self._model.is_open(): return
        
        # Check to see if a file exists with current name
        # If so, we need to add a version extenstion, e.g. (1), (2)
        file_path_list = self._model.get_curr_filename().split("/")
        base_name_arr = file_path_list.pop(-1).split(".")
        name = base_name_arr[0]
        ext = base_name_arr[1]
        str_slash = "/"
        directory_path = str_slash.join(file_path_list)
        i = 1
        curr_name = name

        while(1):
            if not os.path.exists(directory_path + "/" + curr_name + "." + ext):
                break
            curr_name = name + " (" + str(i) + ")" 
            i += 1

        # Set this name as placeholder in save dialog
        filename = self._view.show_save_dialog(curr_name + "." + ext, directory_path)
        
        if filename != None:
            # Check returned value from save dialog to make sure it has a valid extension
            filename = self._check_extension(filename, ext)
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
