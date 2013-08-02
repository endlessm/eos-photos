import sys
import os
from gi.repository import Gtk, Gdk, GLib, GtkClutter, GObject, Gio, Endless

import gettext
gettext.install('endless_photos')

from photos_model import PhotosModel
from photos_view import PhotosView
from photos_presenter import PhotosPresenter


class EndlessPhotos(Endless.Application):
    # ABS_PHOTOS_PATH = '/usr/share/endless-os-photos'
    ABS_PHOTOS_PATH = '.'
    """
    The photo application.

    This class ensures uniqueness (if a second photo application is started
    up, just switch to the first one instead.)

    Currently it is a Gtk.Application, but it should be an Endless.Application.
    """
    __gtype_name__ = 'EndlessPhotos'

    def __init__(self):
        GLib.threads_init()
        Gdk.threads_init()
        GtkClutter.init([])
        Gtk.Application.__init__(self,
                                 application_id='com.endlessm.endless-photos',
                                 flags=Gio.ApplicationFlags.HANDLES_OPEN)

    def do_startup(self):
        """
        Overrides the default Gio.Application.startup handler.

        This code is executed whenever the application starts up; we create the
        main window here.
        """
        # Chaining up is required
        Gtk.Application.do_startup(self)

        # Style CSS
        provider = Gtk.CssProvider()
        provider.load_from_path(self.get_data_path() + 'endless_photos.css')
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        # Create the mvp for the Photo app and attach the window to the
        # application.
        self._model = PhotosModel(
            textures_path=self.get_images_path() + "textures/",
            curves_path=self.get_data_path() + "curves/",
            borders_path=self.get_images_path() + "borders/")
        self._view = PhotosView(application=self, images_path=self.get_images_path())
        self._presenter = PhotosPresenter(model=self._model, view=self._view)
        self._window = self._view.get_window()
        self.add_window(self._window)
        self._window.show_all()
        # hacky way of handling file open args as the proper way has python
        # binding issues.
        for arg in sys.argv[1:]:
            if (not arg[0] == '-') and os.path.exists(arg):
                self._presenter.open_image(arg)
                break

    # This is the proper way to handle opening files, but it doesn't work with
    # the python bindings. The file list is always empty. This is a known bug
    # that may be fixed in newer versions of GTK
    def do_open(self, files, nfiles, hint):
        # print files # always empty
        pass

    def do_activate(self):
        """
        Overrides the default Gio.Application.activate handler.

        It is required to override this in a subclass of Gio.Application, but it
        does not do anything right now.
        """
        self._window.deiconify()

    def get_images_path(self):
        """
        Returns path in the file system where application-specific image files
        are stored.
        """
        return self.ABS_PHOTOS_PATH + '/images/'

    def get_data_path(self):
        """
        Returns path in the file system where application-specific data files
        are stored.
        """
        return self.ABS_PHOTOS_PATH + '/data/'
