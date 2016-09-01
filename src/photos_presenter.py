from datetime import datetime
import errno
import os
import tempfile
import urllib2
import time
from gi.repository import GLib, Gtk, Gio

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

        #Clean out background_images directory
        self._run_locking_task(self._clean_background_dir)

        #set up social bar so we can connect to facebook
        self._facebook_post = FacebookPost()

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
        self._view.lock_ui()

    def _unlock_ui(self):
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

    def _clean_background_dir(self):
        cache_path = GLib.get_user_cache_dir()
        background_images_dir = os.path.join(cache_path, "com.endlessm.photos", "background_images")

        # If directory doesn't exist yet, just return. It will get created
        # when user first sets a background image
        if not os.path.isdir(background_images_dir):
            return
        files = os.listdir(background_images_dir)

        # Sort all background image filenames by last modified timestamp
        decorated = [(filename, os.path.getmtime(os.path.join(background_images_dir, filename))) for filename in files]
        sorted_files = sorted(decorated, key=lambda file_tuple: file_tuple[1], reverse=True)

        # Delete all background images except the most recent 5
        [os.remove(os.path.join(background_images_dir, filename[0])) for filename in sorted_files[5:]]

    def _get_image_tempfile(self):
        # PNG would give no loss from current image, but a lot bigger.
        # Would take longer to upload to facebook/gmail.
        return tempfile.mkstemp('.jpg')[1].lower()

    def _do_post_to_facebook(self, photo_message):
        filename = self._get_image_tempfile()
        self._model.save(filename)
        success, message = self._facebook_post.post_image(filename, photo_message)
        os.remove(filename)
        if message:
            self._view.update_async(lambda: self._view.show_message(text=message, warning=True))

    def _do_set_image_as_background(self):
        filename = self.generate_hashed_filename()
        self._model.save(filename)

        file_uri = "file://" + filename
        settings = Gio.Settings('org.gnome.desktop.background')
        settings.set_string('picture-uri', file_uri)

        self._view.update_async(lambda: self._view.show_message(text=_("Image successfully applied to background!")))

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

    def _open_handler(self, filename):
        self.open_image(filename)

    def _do_open(self):
        pictures_path = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_PICTURES)
        if os.path.isdir(pictures_path):
            self._view.show_open_dialog(pictures_path, self._open_handler)
        else:
            self._view.show_open_dialog(None, self._open_handler)

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

    def _do_rotate(self):
        self._do_crop_cancel()
        self._model.do_rotate()

    def _do_crop_activate(self):
        self._model.do_crop_activate()
        self._view._transformations.open_crop_options()

    def _do_crop_apply(self):
        self._model.do_crop_apply()
        self._view._transformations.close_crop_options()

    def _do_crop_cancel(self):
        if self._model.is_crop_active():
            self._model.do_crop_cancel()
            self._view._transformations.close_crop_options()

    #UI callbacks...

    def on_close(self):
        # Prompt for save before quitting
        if not self._model.is_saved():
            self._view.show_confirm_close(self.on_save, self._view.close_window)
        else:
            self._view.close_window()

    def on_open(self, filename=None):

        # Cancel any ongoing crops
        self._do_crop_cancel()

        if filename is None:
            callback = self._do_open
        else:
            callback = lambda: self.open_image(filename)

        if not self._model.is_saved():
            self._view.show_confirm_open_new_dialog(self.on_save, callback)
        else:
            callback()

    def generate_hashed_filename(self):
        cache_path = GLib.get_user_cache_dir()
        background_images_dir = os.path.join(cache_path, "com.endlessm.photos", "background_images")
        # Check to see if directory for background images exists
        # If doesn't exist yet, recursively create it
        if not os.path.isdir(background_images_dir):
            os.makedirs(background_images_dir)

        # Hash the filename + current timestamp to get unique filename for this background image
        ext = self._model.get_current_filename().split(".")[-1]
        digest_filename = str(hash(self._model.get_current_filename() + datetime.now().__repr__())) + "." + ext
        path = os.path.join(background_images_dir, digest_filename)
        return path


    def generate_filename(self, suffix=None, overwrite=False):
        pictures_path = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_PICTURES)

        # Check to see if a file exists with current name
        # If so, we need to add a version extenstion, e.g. (1), (2)
        file_path_list = self._model.get_current_filename().split("/")
        base_name_arr = file_path_list.pop(-1).split(".")
        if suffix == None:
            name = base_name_arr[0]
        else:
            name = base_name_arr[0] + '_' + suffix
        ext = base_name_arr[1]
        i = 1
        curr_name = name

        while(not overwrite):
            if not os.path.exists(pictures_path + "/" + curr_name + "." + ext):
                break
            curr_name = name + " (" + str(i) + ")"
            i += 1
        return [curr_name, ext]

    def _save_handler(self, filename):
        ext = self._model.get_current_filename().split('.')[-1]
        filename = self._check_extension(filename, ext)
        try:
            self._model.save(filename, save_point=True)
            return True
        except IOError as ex:
            if ex.errno == errno.EACCES or ex.errno == errno.EROFS:
                error_message = _("You do not have permissions to save the photo here")
            else:
                error_message = _("An error occurred while saving your photo")

            self._view.show_message(text=error_message, warning=True)

            return False

    def on_save(self):
        if not self._model.is_open():
            return

        # Cancel any ongoing crops
        self._do_crop_cancel()

        pictures_path = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_PICTURES)

        [curr_name, ext] = self.generate_filename()

        filename = self._view.show_save_dialog(curr_name + "." + ext,
                                               pictures_path,
                                               self._save_handler)

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

    def facebook_login_handler(self, message_to_post, token, dialog_message):
        if token:
            self._facebook_post.login(token)
            if dialog_message:
                self._view.show_message(text=dialog_message, warning=True)
            self._run_locking_task(self._do_post_to_facebook, (message_to_post,))

    def facebook_message_callback(self, confirm, info):
        if confirm != Gtk.ResponseType.OK or info is None:
            return
        logged_in = self._facebook_post.is_logged_in()
        # If not logged in try once to log in
        if not logged_in:
            self._view.show_facebook_login_dialog(info[0])
        else:
            self._run_locking_task(self._do_post_to_facebook, (info[0],))

    def on_share(self):
        if not self._model.is_open():
            return

        # Cancel any ongoing crops
        self._do_crop_cancel()
        self._run_locking_task(self._check_internet_for_facebook_post)

    def _check_internet_for_facebook_post(self):
        if not self.has_internet():
            self._view.update_async(lambda:
                self._view.show_message(text=_("Facebook is not available offline."),
                                        warning=True)
            )
        else:
            self._view.update_async(lambda:
                self._view.get_message(_("Post to Facebook"),
                                       self.facebook_message_callback,
                                       _("Write a description for the photo"))
            )

    def on_set_background(self):
        if not self._model.is_open():
            return

        # Cancel any ongoing crops
        self._do_crop_cancel()
        
        self._run_locking_task(self._do_set_image_as_background)

    def email_message_callback(self, confirm, info):
        if info:
            self._run_locking_task(self._do_send_email, (info[0], info[1], info[2]))

    def on_email(self):
        if not self._model.is_open():
            return

        # Cancel any ongoing crops
        self._do_crop_cancel()

        self._view.get_message(_("Enter a message to add to the e-mail"), self.email_message_callback, _("Your Name:"), _("Recipient email:"), _("Message:"))

    def on_fullscreen(self):
        if not self._model.is_open():
            return
        self._view.set_image_fullscreen(True)

    def on_unfullscreen(self):
        self._view.set_image_fullscreen(False)

    def on_filter_select(self, filter_name):
        if not self._model.is_open():
            return
        self._run_locking_task(self._do_filter_select, (filter_name,))

    def on_blur_select(self, blur_name):
        if not self._model.is_open():
            return
        self._run_locking_task(self._do_blur_select, (blur_name,))

    def on_rotate(self):
        if not self._model.is_open():
            return
        self._run_locking_task(self._do_rotate)

    def on_crop_activate(self):
        if not self._model.is_open():
            return
        self._run_locking_task(self._do_crop_activate)

    def on_crop_apply(self):
        if not self._model.is_open():
            return
        self._run_locking_task(self._do_crop_apply)

    def on_crop_cancel(self):
        if not self._model.is_open():
            return
        self._run_locking_task(self._do_crop_cancel)

    def on_border_select(self, border_name):
        if not self._model.is_open():
            return
        self._model.set_border(border_name)
        self._view.select_border(border_name)

    def on_distortion_select(self, distort_name):
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
        self._make_adjustment_change(
            value, self._model.get_contrast, self._model.set_contrast, "Contrast Slider Thread")

    def on_brightness_change(self, value):
        self._make_adjustment_change(
            value, self._model.get_brightness, self._model.set_brightness, "Brightness Slider Thread")

    def on_saturation_change(self, value):
        self._make_adjustment_change(
            value, self._model.get_saturation, self._model.set_saturation, "Saturation Slider Thread")

    def on_tilt_shift_toggle(self, toggleAction, (coord_x, coord_y)):
        if not self._model.is_open():
            return
        if toggleAction.get_active():
            self._run_locking_task(self._do_blur_select, ("TILT-SHIFT",))

    def on_depth_of_field_toggle(self, toggleAction, (coord_x, coord_y)):
        if not self._model.is_open():
            return
        if toggleAction.get_active():
            self._run_locking_task(self._do_blur_select, ("DEPTH-OF-FIELD",))

    def on_noblur_toggle(self, toggleAction):
        if not self._model.is_open():
            return
        if toggleAction.get_active():
            self._run_locking_task(self._do_blur_select, ("NONE",))

    def on_revert(self):
        self._do_crop_cancel()
        self._model.revert_to_original()
        self._sync_photo_options()
