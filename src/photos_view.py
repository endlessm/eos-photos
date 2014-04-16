from gi.repository import Gtk, Gdk, GLib

from splash_screen import SplashScreen
from photos_left_toolbar import PhotosLeftToolbar
from photos_right_toolbar import PhotosRightToolbar
from photos_category_toolbars import AdjustmentToolbar, BorderToolbar, FilterToolbar, DistortToolbar, BlurToolbar, TransformToolbar
from photos_window import PhotosWindow
from photos_image_container import ImageContainer
from widgets.preview_file_chooser_dialog import PreviewFileChooserDialog
from share.facebook_auth_dialog import FacebookAuthDialog


class PhotosView(object):
    """
    The main view class for the photo application. Mainly just passes the
    presenter calls to the appropriate UI elements. PhotosWindow does the
    actual toplevel layout of the toolbars and central view.
    """
    def __init__(self, application=None, images_path=""):
        self._images_path = images_path
        self._adjustments = AdjustmentToolbar(images_path=images_path)
        self._blurs = BlurToolbar(images_path=images_path)
        self._transformations = TransformToolbar(images_path=images_path)
        self._filters = FilterToolbar(images_path=images_path)
        self._borders = BorderToolbar(images_path=images_path)
        self._distorts = DistortToolbar(images_path=images_path)
        categories = [self._transformations, self._adjustments, self._filters, self._distorts, self._blurs, self._borders]
        self._left_toolbar = PhotosLeftToolbar(images_path=images_path,
                                               categories=categories)
        self._splash_screen = SplashScreen(name="splash-eventbox")

        self._right_toolbar = PhotosRightToolbar()
        self._image_container = ImageContainer(images_path=images_path, name="image-container")
        self._window = PhotosWindow(images_path=images_path,
                                    splash_screen=self._splash_screen,
                                    left_toolbar=self._left_toolbar,
                                    right_toolbar=self._right_toolbar,
                                    image_container=self._image_container,
                                    application=application)

    def set_presenter(self, presenter):
        self._presenter = presenter
        self._splash_screen.set_presenter(presenter)
        self._left_toolbar.set_presenter(presenter)
        self._right_toolbar.set_presenter(presenter)
        self._image_container.set_presenter(presenter)
        self._blurs.set_presenter(presenter)
        self._transformations.set_presenter(presenter)
        self._adjustments.set_presenter(presenter)
        self._borders.set_presenter(presenter)
        self._filters.set_presenter(presenter)
        self._distorts.set_presenter(presenter)
        self._window.set_presenter(presenter)

    # This should be called to update the UI from outside of GTK's thread. It
    # will call an update function fn to be called on the main thread at the
    # next opportunity.
    def update_async(self, fn):
        Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, lambda dummy: fn(), None)

    def get_window(self):
        return self._window

    def close_window(self):
        self._window.destroy()

    def minimize_window(self):
        self._window.iconify()

    def set_image_widget(self, widget):
        self._image_container.set_image_widget(widget)
        widget._crop_overlay._crop_box.set_view(self)

    def set_cursor(self, cursor):
        if cursor is not None:
            self.get_window().get_window().set_cursor(cursor)

    def set_photo_editor_active(self):
        self._window.set_photo_editor_active()

    def set_image_fullscreen(self, fullscreen):
        self._window.set_image_fullscreen(fullscreen)

    def set_filters(self, filters):
        self._filters.set_options(filters)

    def set_blurs(self, blurs):
        self._blurs.set_blurs(blurs)

    def set_transformations(self, transformations):
        self._transformations.set_transformations(transformations)

    def set_borders(self, borders):
        self._borders.set_options(borders)

    def set_distortions(self, distortions):
        self._distorts.set_options(distortions)

    def select_filter(self, filter_name):
        self._filters.select(filter_name)

    def select_blur(self, blur_name):
        self._blurs.select(blur_name)

    def select_transformation(self, transformation_name):
        self._transformations.select(transformation_name)

    def select_border(self, border_name):
        self._borders.select(border_name)

    def select_distortion(self, distort_name):
        self._distorts.select(distort_name)

    def set_brightness_slider(self, value):
        self._adjustments.set_brightness_slider(value)

    def set_contrast_slider(self, value):
        self._adjustments.set_contrast_slider(value)

    def set_saturation_slider(self, value):
        self._adjustments.set_saturation_slider(value)

    def facebook_login_callback(self, dialog, response, message_to_post):
        self._presenter.facebook_login_handler(message_to_post, dialog.get_access_token(), dialog.get_message())
        dialog.hide()

    def show_facebook_login_dialog(self, message_to_post):
        dialog = FacebookAuthDialog(transient_for=self.get_window())
        dialog.connect('response', self.facebook_login_callback, message_to_post)
        dialog.show()

    def open_callback(self, dialog, response):
        if response == Gtk.ResponseType.ACCEPT:
            self._presenter.open_handler(
                dialog.get_filename())
        dialog.hide()

    def show_open_dialog(self, starting_dir=None):
        # Opens a dialog window where the user can choose an image file
        dialog = PreviewFileChooserDialog(
            title=_("Open Image"),
            parent=self.get_window(),
            action=Gtk.FileChooserAction.OPEN,
            modal=True)

        if starting_dir != None:
            dialog.set_current_folder(starting_dir)

        # Adds 'Cancel' and 'OK' buttons
        dialog.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT)
        dialog.add_button(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT)

        # Sets default to 'OK'
        dialog.set_default_response(Gtk.ResponseType.ACCEPT)

        # Filters and displays files which can be opened by Gtk.Image
        filefilter = Gtk.FileFilter()
        filefilter.add_pixbuf_formats()
        dialog.set_filter(filefilter)

        dialog.connect('response', self.open_callback)

        dialog.show()

    def save_callback(self, dialog, response):
        if response == Gtk.ResponseType.ACCEPT:
            should_close = self._presenter.save_handler(
                dialog.get_filename())
            if should_close:
                dialog.hide()
        else:
            dialog.hide()

    def show_save_dialog(self, curr_name, dir_path):
        # Opens a dialog window where the user can choose an image file
        dialog = Gtk.FileChooserDialog(
            _("Save Image"),
            self.get_window(),
            Gtk.FileChooserAction.SAVE,
            modal=True)
        dialog.set_do_overwrite_confirmation(True);

        # Adds 'Cancel' and 'OK' buttons
        dialog.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT)
        dialog.add_button(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT)

        dialog.set_current_folder(dir_path)
        dialog.set_current_name(curr_name)
        # Sets default to 'OK'
        dialog.set_default_response(Gtk.ResponseType.ACCEPT)

        dialog.connect('response', self.save_callback)
        dialog.show()

    def confirm_open_new_callback(self, dialog, response):
        dialog.hide()
        if response == 1:
            self._presenter._do_open()

    def show_confirm_open_new_dialog(self):
        dialog = Gtk.MessageDialog(
            parent=self.get_window(),
            text=_("Open new photo without save?"),
            secondary_text=_("Your changes have not been saved. Are you sure you want to open a new photo without saving?"),
            message_type=Gtk.MessageType.WARNING,
            modal=True)
        dialog.add_button(Gtk.STOCK_CANCEL, 0)
        dialog.add_button(Gtk.STOCK_OK, 1)
        # set default to cancel
        dialog.set_default_response(0)
        dialog.connect('response', self.confirm_open_new_callback)
        dialog.show()

    def confirm_close_callback(self, dialog, response):
        dialog.hide()
        if response == 1:
            self._presenter.on_save()
        elif response == 2:
            self.close_window()

    def show_confirm_close(self):
        dialog = Gtk.MessageDialog(
            parent=self.get_window(),
            text=_("Quit Without Save?"),
            secondary_text=_("Your changes have not been saved. Are you sure you want to quit?"),
            message_type=Gtk.MessageType.WARNING,
            modal=True)
        dialog.add_button(Gtk.STOCK_CANCEL, 0)
        dialog.add_button(Gtk.STOCK_SAVE, 1)
        dialog.add_button(Gtk.STOCK_QUIT, 2)
        # set default to cancel
        dialog.set_default_response(0)
        dialog.connect('response', self.confirm_close_callback)
        dialog.show()

    def show_message(self, text="", secondary_text="", warning=False):
        dialog_type = Gtk.MessageType.WARNING if warning else Gtk.MessageType.INFO
        dialog = Gtk.MessageDialog(
            parent=self.get_window(),
            text=text,
            secondary_text=secondary_text,
            message_type=dialog_type,
            modal=True)
        dialog.add_button(Gtk.STOCK_OK, 0)
        # set default to cancel
        dialog.set_default_response(0)
        dialog.connect('response', lambda dialog, response: dialog.hide())
        dialog.show()

    def message_callback(self, dialog, confirm, entries, callback):
        responses = []
        map(lambda x: responses.append(x.get_text()), entries)
        dialog.hide()
        if confirm <= 0:
            confirm = 0
        callback(confirm, responses)

    # Gets responses from a user. Args is a list of requested responses
    # from the user.
    def get_message(self, prompt, callback, *args):
        dialog = Gtk.MessageDialog(
            image=None,
            parent=self.get_window(),
            use_markup=True,
            message_type=Gtk.MessageType.WARNING,
            modal=True)
        dialog.set_markup("<big><b>" + prompt + "</b></big>")
        dialog.add_button(Gtk.STOCK_OK, 1)
        dialog.add_button(Gtk.STOCK_CANCEL, 0)
        dialog.set_default_response(1)
        dialog.set_size_request(400, -1)

        entries = []
        # Create an entry for each of the requested responses
        for msg in args:
            entry = Gtk.Entry()
            entry.set_size_request(-1, 30)
            entry.set_activates_default(True)
            entries.append(entry)
            align = Gtk.Alignment(xalign=0, yalign=0, xscale=0, yscale=0)
            align.add(Gtk.Label(msg))
            vbox = Gtk.VBox()
            vbox.pack_start(align, False, 5, 5)
            vbox.pack_end(entry, True, True, 0)
            dialog.get_message_area().pack_start(vbox, True, True, 0)

        dialog.connect('response', self.message_callback, entries, callback)
        dialog.show_all()

    def lock_ui(self):
        # TODO: bring set_sensitive back someday!!! When we know why it breaks
        # things
        watch = Gdk.Cursor(Gdk.CursorType.WATCH)
        gdk_window = self._window.get_window()
        gdk_window.set_cursor(watch)
        # self._window.set_sensitive(False)

    def unlock_ui(self):
        pointer = Gdk.Cursor(Gdk.CursorType.ARROW)
        gdk_window = self._window.get_window()
        gdk_window.set_cursor(pointer)
        self._window.queue_draw()
        # self._window.set_sensitive(True)
