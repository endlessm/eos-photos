import os
import tempfile
import urllib2
import time
from gi.repository import GLib

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
        self._view.set_image_widget(self._model.get_image_widget())
        filters = self._model.get_filter_names_and_thumbnails()
        self._view.set_filters(filters)
        borders = self._model.get_border_names_and_thumbnails()
        self._view.set_borders(borders)
        blurs = self._model.get_blur_names_and_thumbnails()
        self._view.set_blurs(blurs)
        distortions = self._model.get_distortion_names_and_thumbnails()
        self._view.set_distortions(distortions)

        #Track threads in use
        self._active_threads = []

        #set up social bar so we can connect to facebook
        self._facebook_post = FacebookPost()
        self._locked = False

    def open_image(self, filename):
        self._model.open(filename)
        self._sync_photo_options()
        self._view.set_photo_editor_active()

    def _sync_photo_options(self):
        self._view.select_filter(self._model.get_filter())
        self._view.select_border(self._model.get_border())
        self._view.select_distortion(self._model.get_distortion())
        self._view.select_blur(self._model.get_blur())
        self._view.set_brightness_slider(self._model.get_brightness())
        self._view.set_contrast_slider(self._model.get_contrast())
        self._view.set_saturation_slider(self._model.get_saturation())

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
        self._locked = True
        self._view.lock_ui()

    def _unlock_ui(self):
        self._locked = False
        self._view.unlock_ui()

    def _run_locking_task(self, method, args=()):
        worker = AsyncWorker()
        worker.add_task(self._view.update_async, (self._lock_ui,))
        worker.add_task(method, args)
        worker.add_task(self._view.update_async, (self._unlock_ui,))
        worker.start()

    def _run_non_locking_task(self, method, args=(), name=""):
        worker = AsyncWorker(name)
        worker.add_task(method, args)
        worker.start()
        self._active_threads.append(worker)

    def _get_image_tempfile(self):
        # PNG would give no loss from current image, but a lot bigger.
        # Would take longer to upload to facebook/gmail.
        return tempfile.mkstemp('.jpg')[1].lower()

    def _do_post_to_facebook(self, photo_message):
        success = True
        if not self._facebook_post.is_user_loged_in():
            success, err_message = self._facebook_post.fb_login()
        if success:
            filename = self._get_image_tempfile()
            self._model.save(filename)
            success, message = self._facebook_post.post_image(filename, photo_message)
            os.remove(filename)
        if not success:
            self._view.update_async(lambda: self._view.show_message(text=_(err_message), warning=True))

    def _do_send_email(self, name, recipient, message):
        filename = self._get_image_tempfile()
        self._model.save(filename)
        if not share.emailer.email_photo(name, recipient, message, filename):
            self._view.update_async(lambda: self._view.show_message(text=_("Email failed."), warning=True))
        os.remove(filename)

    def _do_filter_select(self, filter_name):
        self._model.set_filter(filter_name)
        self._view.update_async(lambda: self._view.select_filter(filter_name))

    def _do_distort(self, distort_name):
        self._model.set_distortion(distort_name)
        self._view.update_async(lambda: self._view.select_distortion(distort_name))

    def _do_open(self):
        pictures_path = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_PICTURES)
        if os.path.isdir(pictures_path):
            filename = self._view.show_open_dialog(pictures_path)
        else:
            filename = self._view.show_open_dialog()
        if filename is not None:
            self.open_image(filename)

    def _do_adjustment_slide(self, value_get, value_set):
        in_timeout = False
        while True:
            if in_timeout and time.time() - start_time > 0.2:
                break
            if self._slider_target == value_get():
                if not in_timeout:
                    in_timeout = True
                    start_time = time.time()
                else:
                    time.sleep(0.001)
            else:
                value_set(self._slider_target)
                in_timeout = False

    def _do_blur_select(self, blur_type):
        self._model.set_blur(blur_type)
        self._view.update_async(lambda: self._view.select_blur(blur_type))

    #UI callbacks...
    def on_close(self):
        if self._locked:
            return
        # Prompt for save before quitting
        if not self._model.is_saved():
            confirm = self._view.show_confirm_close()
            if not confirm:
                return
            elif confirm == 1:
                self.on_save()

        self._view.close_window()

    def on_minimize(self):
        if self._locked:
            return
        self._view.minimize_window()

    def on_open(self):
        if self._locked:
            return
        if not self._model.is_saved():
            confirm = self._view.show_confirm_open_new()
            if not confirm:
                return
        self._do_open()

    def on_save(self):
        if self._locked:
            return
        if not self._model.is_open():
            return

        # Check to see if a file exists with current name
        # If so, we need to add a version extenstion, e.g. (1), (2)
        file_path_list = self._model.get_current_filename().split("/")
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

    def has_internet(self):
        '''
        If Google is down, this will generate false negatives.
        '''
        try:
            test_request = urllib2.Request("http://www.google.com")
            urllib2.urlopen(test_request)
            return True
        except:
            return False

    def on_share(self):
        if self._locked:
            return
        if not self._model.is_open():
            return
        if not self.has_internet():
            self._view.update_async(lambda: self._view.show_message(text=_("Facebook is not available offline."), warning=True))
            return
        info = self._view.get_message(_("Enter a message to add to your photo!"), _("Message:"))
        if info:
            self._run_locking_task(self._do_post_to_facebook, (info[0],))

    def on_email(self):
        if self._locked:
            return
        if not self._model.is_open():
            return
        info = self._view.get_message(_("Enter a message to add to the e-mail"), _("Your Name:"), _("Recipient email:"), _("Message:"))
        if info:
            self._run_locking_task(self._do_send_email, (info[0], info[1], info[2]))

    def on_fullscreen(self):
        if self._locked:
            return
        if not self._model.is_open():
            return
        self._view.set_image_fullscreen(True)

    def on_unfullscreen(self):
        if self._locked:
            return
        self._view.set_image_fullscreen(False)

    def on_filter_select(self, filter_name):
        if self._locked:
            return
        if not self._model.is_open():
            return
        self._run_locking_task(self._do_filter_select, (filter_name,))

    def on_blur_select(self, blur_name):
        if self._locked:
            return
        if not self._model.is_open():
            return
        self._run_locking_task(self._do_blur_select, (blur_name,))

    def on_border_select(self, border_name):
        if self._locked:
            return
        if not self._model.is_open():
            return
        self._model.set_border(border_name)
        self._view.select_border(border_name)

    def on_distortion_select(self, distort_name):
        if self._locked:
            return
        if not self._model.is_open():
            return
        self._run_locking_task(self._do_distort, (distort_name,))

    def _prune_active_threads(self):
        ''' Clears out old threads from the
        active thread list. ''' 
        self._active_threads = [x for x in self._active_threads if x.finished == False]

    def _active_thread_exists(self, thread_name):
        ''' Returns true if a thread with the given name already
        exists. '''
        self._prune_active_threads()
        return thread_name in [x.name for x in self._active_threads] 

    def _make_adjustment_change(self, value, get_func, set_func, thread_name="Slider Thread"):
        if not self._model.is_open():
            return
        self._slider_target = value
        if not self._active_thread_exists(thread_name):
            self._run_non_locking_task(
                self._do_adjustment_slide,
                (get_func, set_func),
                thread_name)

    def on_contrast_change(self, value):
        if self._locked:
            return
        self._make_adjustment_change(
            value, self._model.get_contrast, self._model.set_contrast, "Contrast Slider Thread")

    def on_brightness_change(self, value):
        if self._locked:
            return
        self._make_adjustment_change(
            value, self._model.get_brightness, self._model.set_brightness, "Brightness Slider Thread")

    def on_saturation_change(self, value):
        if self._locked:
            return
        self._make_adjustment_change(
            value, self._model.get_saturation, self._model.set_saturation, "Saturation Slider Thread")

    def on_tilt_shift_toggle(self, toggleAction, (coord_x, coord_y)):
        if self._locked:
            return
        if not self._model.is_open():
            return
        if toggleAction.get_active():
            self._run_locking_task(self._do_blur_select, ("TILT-SHIFT",))

    def on_depth_of_field_toggle(self, toggleAction, (coord_x, coord_y)):
        if self._locked:
            return
        if not self._model.is_open():
            return
        if toggleAction.get_active():
            self._run_locking_task(self._do_blur_select, ("DEPTH-OF-FIELD",))

    def on_noblur_toggle(self, toggleAction):
        if self._locked:
            return
        if not self._model.is_open():
            return
        if toggleAction.get_active():
            self._run_locking_task(self._do_blur_select, ("NONE",))

    def on_revert(self):
        if self._locked:
            return
        self._model.clear_options()
        self._sync_photo_options()
