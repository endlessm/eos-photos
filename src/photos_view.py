from gi.repository import Gtk, Gdk

from photos_top_toolbar import PhotosTopToolbar
from photos_left_toolbar import PhotosLeftToolbar
from photos_right_toolbar import PhotosRightToolbar
from photos_adjustment_toolbar import PhotosAdjustmentToolbar
from photos_border_toolbar import PhotosBorderToolbar
from photos_filter_toolbar import PhotosFilterToolbar
from photos_window import PhotosWindow
from photos_image_viewer import ImageViewer


class PhotosView(object):
    """
    The main view class for the photo application. Mainly just passes the
    presenter calls to the appropriate UI elements. PhotosWindow does the
    actual toplevel layout of the toolbars and central view.
    """
    def __init__(self, images_path=""):
        self._adjustments = PhotosAdjustmentToolbar(images_path=images_path)
        self._borders = PhotosBorderToolbar(images_path=images_path)
        self._filters = PhotosFilterToolbar(images_path=images_path)
        self._left_toolbar = PhotosLeftToolbar(images_path=images_path,
                                               adjustments=self._adjustments,
                                               borders=self._borders,
                                               filters=self._filters)
        self._top_toolbar = PhotosTopToolbar(images_path=images_path)
        self._right_toolbar = PhotosRightToolbar(images_path=images_path)
        self._image_viewer = ImageViewer(images_path=images_path)
        self._window = PhotosWindow(images_path=images_path,
                                    top_toolbar=self._top_toolbar,
                                    left_toolbar=self._left_toolbar,
                                    right_toolbar=self._right_toolbar,
                                    image_viewer=self._image_viewer)

    def set_presenter(self, presenter):
        self._presenter = presenter
        self._top_toolbar.set_presenter(presenter)
        self._left_toolbar.set_presenter(presenter)
        self._right_toolbar.set_presenter(presenter)
        self._image_viewer.set_presenter(presenter)
        self._adjustments.set_presenter(presenter)
        self._borders.set_presenter(presenter)
        self._filters.set_presenter(presenter)

    def get_window(self):
        return self._window

    def close_window(self):
        self._window.destroy()

    def minimize_window(self):
        self._window.iconify()

    def set_image_fullscreen(self, fullscreen):
        self._window.set_image_fullscreen(fullscreen)

    def set_filters(self, filters):
        self._filters.set_filters(filters)

    def select_filter(self, filter_name):
        self._filters.select_filter(filter_name)

    def select_border(self, border_name):
        self._borders.select_border(border_name)

    def replace_image_from_file(self, image_name):
        self._image_viewer.load_from_file(image_name)

    def replace_image_from_pixbuf(self, image_name):
        self._image_viewer.load_from_pixbuf(image_name)

    def replace_image_from_data(self, data, width, height):
        self._image_viewer.load_from_data(data, width, height)

    def show_open_dialog(self):
        # Opens a dialog window where the user can choose an image file
        dialog = Gtk.FileChooserDialog(
            _("Open Image"), self.get_window(),
            Gtk.FileChooserAction.OPEN)

        # Adds 'Cancel' and 'OK' buttons
        dialog.add_button(Gtk.STOCK_CANCEL, 0)
        dialog.add_button(Gtk.STOCK_OK, 1)

        # Sets default to 'OK'
        dialog.set_default_response(1)

        # Filters and displays files which can be opened by Gtk.Image
        filefilter = Gtk.FileFilter()
        filefilter.add_pixbuf_formats()
        dialog.set_filter(filefilter)

        if dialog.run() == 1:
            # Loads the image
            filename = dialog.get_filename()
            dialog.destroy()
            return filename
        else:
            dialog.destroy()
            return None

    def show_save_dialog(self, curr_name, dir_path):
        # Opens a dialog window where the user can choose an image file
        dialog = Gtk.FileChooserDialog(_("Save Image"), self.get_window(), Gtk.FileChooserAction.SAVE)

        # Adds 'Cancel' and 'OK' buttons
        dialog.add_button(Gtk.STOCK_CANCEL, 0)
        dialog.add_button(Gtk.STOCK_OK, 1)

        dialog.set_current_folder(dir_path)
        dialog.set_current_name(curr_name)
        # Sets default to 'OK'
        dialog.set_default_response(1)

        if dialog.run() == 1:
            # Loads the image
            filename = dialog.get_filename()
            dialog.destroy()
            return filename
        else:
            dialog.destroy()
            return None

    def show_confirm_open_new(self):
        dialog = Gtk.MessageDialog(
            parent=self.get_window(),
            text=_("Open New Photo Without Save?"),
            secondary_text=_("Your changes have not been saved. Are you sure you want to open a new photo without saving?"),
            message_type=Gtk.MessageType.WARNING)
        dialog.add_button(Gtk.STOCK_CANCEL, 0)
        dialog.add_button(Gtk.STOCK_OK, 1)
        # set default to cancel
        dialog.set_default_response(0)
        confirm = dialog.run()
        dialog.destroy()
        return confirm

    def show_confirm_close(self):
        dialog = Gtk.MessageDialog(
            parent=self.get_window(),
            text=_("Quit Without Save?"),
            secondary_text=_("Your changes have not been saved. Are you sure you want to quit?"),
            message_type=Gtk.MessageType.WARNING)
        dialog.add_button(Gtk.STOCK_CANCEL, 0)
        dialog.add_button(Gtk.STOCK_SAVE, 1)
        dialog.add_button(Gtk.STOCK_QUIT, 2)
        # set default to cancel
        dialog.set_default_response(0)
        confirm = dialog.run()
        dialog.destroy()
        return confirm

    def show_message(self, text="", secondary_text="", warning=False):
        dialog_type = Gtk.MessageType.WARNING if warning else Gtk.MessageType.INFO
        dialog = Gtk.MessageDialog(
            parent=self.get_window(),
            text=text,
            secondary_text=secondary_text,
            message_type=dialog_type)
        dialog.add_button(Gtk.STOCK_OK, 0)
        # set default to cancel
        dialog.set_default_response(0)
        dialog.run()
        dialog.destroy()

    # Gets responses from a user. Args is a list of requested responses
    # from the user.
    def get_message(self, prompt, *args):
        dialog = Gtk.MessageDialog(
            self.get_window(), 0,
            Gtk.MessageType.OTHER, Gtk.ButtonsType.OK_CANCEL,
            prompt)
        dialog.set_default_response(Gtk.ResponseType.OK)

        entries = []
        # Create an entry for each of the requested responses
        for msg in args:
            entry = Gtk.Entry()
            entries.append(entry)
            hbox = Gtk.HBox()
            hbox.pack_start(Gtk.Label(msg), False, 5, 5)
            hbox.pack_end(entry, True, True, 0)
            dialog.vbox.pack_start(hbox, True, True, 0)

        dialog.show_all()
        result = dialog.run()

        # If user clicks cancel, return having done nothing
        if result == Gtk.ResponseType.CANCEL:
            dialog.destroy()
            return None

        # Store the responses from user in this list
        responses = []
        map(lambda x: responses.append(x.get_text()), entries)
        dialog.destroy()
        return responses

    def show_spinner(self):
        watch = Gdk.Cursor(Gdk.CursorType.WATCH)
        gdk_window = self._window.get_window()
        gdk_window.set_cursor(watch)

    def hide_spinner(self):
        pointer = Gdk.Cursor(Gdk.CursorType.ARROW)
        gdk_window = self._window.get_window()
        gdk_window.set_cursor(pointer)
        self._window.queue_draw()
