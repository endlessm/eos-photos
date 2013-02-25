import sys, os
from gi.repository import Gtk, Gdk, GLib, GtkClutter, GObject, Gio


import gettext
gettext.install('endless_photos')

from photos_model import PhotosModel
from photos_view import PhotosView
from photos_presenter import PhotosPresenter


class EndlessPhotos(Gtk.Application):
    """
    The photo application.

    This class ensures uniqueness (if a second photo application is started
    up, just switch to the first one instead.)

    Currently it is a Gtk.Application, but it should be an Endless.Application.
    """
    __gtype_name__ = 'EndlessPhotos'

    def __init__(self):
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
        provider.load_from_path('../data/endless_photos.css')
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        # Create the mvp for the Photo app and attach the window to the application.
        self._model = PhotosModel()
        self._view = PhotosView()
        self._presenter = PhotosPresenter(model=self._model, view=self._view)
        self._window = self._view.get_window()
        self.add_window(self._window)
        self._window.show()
        # hacky way of handling file open args as the proper way has python binding issues.
        for arg in sys.argv[1:]:
            if (not arg[0] == '-') and os.path.exists(arg):
                self._presenter.open_image(arg)
                break


        # Run the main loop, to make sure the window is shown and therefore
        # seems responsive
        while Gtk.events_pending():
            Gtk.main_iteration()

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
        pass

if __name__ == '__main__':
    GObject.threads_init()
    GtkClutter.init([])
    app = EndlessPhotos()
    app.run(sys.argv)
