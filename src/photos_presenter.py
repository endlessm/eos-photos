import os
import tempfile
import array

from asyncworker import AsyncWorker
from share.facebook_post import FacebookPost
import share.emailer

VALID_FILE_TYPES = ["jpg", "png", "gif", "jpeg"]

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
        self._lock = False
        #set up social bar so we can connect to facebook
        self._facebook_post = FacebookPost()


    def _update_view(self):
        im = self._model.get_image().convert('RGBA')
        width, height = im.size
        self._view.replace_image_from_data(im.tostring(),
                                           width, height)
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

    def _lock_ui(self):
        self._lock = True
        self._view.show_spinner()

    def _unlock_ui(self):
        self._lock = False
        self._view.hide_spinner()

    def _run_method_with_handler(self, method, args, callback, callback_args=()):
        method(*args)
        callback(*callback_args)


    def _run_asynch_task(self, method, args):
        self._lock_ui()
        worker = AsyncWorker()
        worker.add_task(method, args)
        worker.add_task(self._unlock_ui, ())       
        worker.start()

    def _do_post_to_facebook(self, message):
        if not self._facebook_post.is_user_loged_in():
            self._facebook_post.fb_login()
        filename = self._model.save_to_tempfile()
        if not self._facebook_post.post_image(filename, message):
            # we need to request this from the gtk main thread...
            # self._view.show_message("Post to facebook failed.")
            print "Post failed."

    def _do_send_email(self, name, recipient, message):
        filename = self._model.save_to_tempfile()
        if not share.emailer.email_photo(name, recipient, message, filename):
            # self._view.show_message("Email failed.")
            print "Email failed"

    #UI callbacks...
    def on_close(self):
        # Prompt for save?
        if self._lock: return 
        if self._model.is_saved():
            self._view.close_window()
        else:
            confirm = self._view.show_confirm_close()
            if confirm:
                self._view.close_window()

    def on_minimize(self):
        if self._lock: return
        self._view.minimize_window()

    def on_open(self):
        if self._lock: return
        filename = self._view.show_open_dialog()
        if filename != None:
            self._model.open(filename)
            self._view.select_filter(self._model.get_default_name())
            self._update_view()

    def on_save(self):
        if self._lock or not self._model.is_open(): return
        
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
        if self._lock or not self._model.is_open(): return
        info = self._view.get_message("Enter a message to add to your photo!", "Message")
        if info:
            self._run_asynch_task(self._do_post_to_facebook, (info[0],))
        
    def on_email(self):
        if self._lock or not self._model.is_open(): return
        info = self._view.get_message("Enter a message to add to the e-mail", "Your Name", "Recipient email", "Message")
        if info:
            self._run_asynch_task(self._do_send_email, (info[0], info[1], info[2]))

    def on_fullscreen(self):
        if self._lock or not self._model.is_open(): return
        self._view.set_image_fullscreen(True)

    def on_unfullscreen(self):
        self._view.set_image_fullscreen(False)

    def on_filter_select(self, filter_name):
        if self._lock or not self._model.is_open(): return
        
        self._model.apply_filter(filter_name)
        self._update_view()
        self._view.select_filter(filter_name)
