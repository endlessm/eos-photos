import os

from gi.repository import Gtk, Gdk

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
        filters = self._model.get_filter_names_and_thumbnails()
        self._view.set_filters(filters)
        self._lock = False
        #set up social bar so we can connect to facebook
        self._facebook_post = FacebookPost()

    def open_image(self, filename):
        self._model.open(filename)
        self._model.reset_options()
        self._view.select_filter(self._model.get_filter())
        self._view.set_brightness_slider(self._model.get_brightness())
        self._view.set_contrast_slider(self._model.get_contrast())
        self._view.set_saturation_slider(self._model.get_saturation())
        # TODO: set border when its implemented.
        self._update_view()

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

        if ext not in VALID_FILE_TYPES:
            return dot_join.join(name_arr) + "." + original_ext
        return filename

    def _lock_ui(self):
        Gdk.threads_enter()
        self._lock = True
        self._view.show_spinner()
        Gdk.threads_leave()

    def _unlock_ui(self):
        Gdk.threads_enter()
        self._lock = False
        self._view.hide_spinner()
        Gdk.threads_leave()

    def _run_method_with_handler(self, method, args, callback, callback_args=()):
        method(*args)
        callback(*callback_args)

    def _run_asynch_task(self, method, args):
        worker = AsyncWorker()
        worker.add_task(self._lock_ui, ())
        worker.add_task(method, args)
        worker.add_task(self._unlock_ui, ())
        worker.start()

    def _do_post_to_facebook(self, message):
        if not self._facebook_post.is_user_loged_in():
            self._facebook_post.fb_login()
        filename = self._model.save_to_tempfile()
        success, message = self._facebook_post.post_image(filename, message)
        if not success:
            Gdk.threads_enter()
            self._view.show_message(text=message, warning=True)
            Gdk.threads_leave()

    def _do_send_email(self, name, recipient, message):
        filename = self._model.save_to_tempfile()
        if not share.emailer.email_photo(name, recipient, message, filename):
            Gdk.threads_enter()
            self._view.show_message(text="Email failed", warning=True)
            Gdk.threads_leave()

    def _do_open(self):
        filename = self._view.show_open_dialog()
        if filename is not None:
            self.open_image(filename)
        # If extension is not a valid file type we use the extension of the original file

    def _do_on_filter_select(self, filter_name):
        self._model.set_filter(filter_name)
        Gdk.threads_enter()
        self._update_view()
        self._view.select_filter(filter_name)
        Gdk.threads_leave()

    #UI callbacks...
    def on_close(self):
        # Prompt for save before quitting
        if self._lock:
            return

        if not self._model.is_saved():
            confirm = self._view.show_confirm_close()
            if not confirm:
                return
            elif confirm == 1:
                self.on_save()

        self._view.close_window()

    def on_minimize(self):
        if self._lock:
            return
        self._view.minimize_window()

    def on_open(self):
        if self._lock:
            return
        if not self._model.is_saved():
            confirm = self._view.show_confirm_open_new()
            if not confirm:
                return
        self._do_open()

    def on_save(self):
        if self._lock or not self._model.is_open():
            return

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

        if filename is not None:
            # Check returned value from save dialog to make sure it has a valid extension
            filename = self._check_extension(filename, ext)
            self._model.save(filename)

    def on_share(self):
        if self._lock or not self._model.is_open():
            return
        info = self._view.get_message(_("Enter a message to add to your photo!"), _("Message"))
        if info:
            self._run_asynch_task(self._do_post_to_facebook, (info[0],))

    def on_email(self):
        if self._lock or not self._model.is_open():
            return
        info = self._view.get_message(_("Enter a message to add to the e-mail"), _("Your Name"), _("Recipient email"), _("Message"))
        if info:
            self._run_asynch_task(self._do_send_email, (info[0], info[1], info[2]))

    def on_fullscreen(self):
        if self._lock or not self._model.is_open():
            return
        self._view.set_image_fullscreen(True)

    def on_unfullscreen(self):
        self._view.set_image_fullscreen(False)

    def on_filter_select(self, filter_name):
        if self._lock or not self._model.is_open():
            return

        # self._run_asynch_task(self._do_on_filter_select, (filter_name,))
        self._model.set_filter(filter_name)
        self._update_view()
        self._view.select_filter(filter_name)

    def on_border_select(self, border_name):
        print border_name, "border selected..."
        self._view.select_border(border_name)

    def on_contrast_change(self, value):
        if self._lock or not self._model.is_open():
            return
        self._model.set_contrast(value)
        self._update_view()

    def on_brightness_change(self, value):
        if self._lock or not self._model.is_open():
            return
        self._model.set_brightness(value)
        self._update_view()

    def on_saturation_change(self, value):
        if self._lock or not self._model.is_open():
            return
        self._model.set_saturation(value)
        self._update_view()
