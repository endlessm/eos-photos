import sys
import os
import inspect
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GtkClutter, GObject, Gio, Endless

from .photos_model import PhotosModel
from .photos_view import PhotosView
from .photos_presenter import PhotosPresenter
from .resource_prefixes import *

CURRENT_FILE = os.path.abspath(inspect.getfile(inspect.currentframe()))
CURRENT_DIR = os.path.dirname(CURRENT_FILE)
ASSET_RESOURCE_PATH = CURRENT_DIR + '/../data/endless_photos.gresource';
THUMBNAIL_RESOURCE_PATH = CURRENT_DIR + '/../data/images/thumbnails/thumbnails.gresource';

class EndlessPhotos(Endless.Application):
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
        Endless.Application.__init__(self,
                                 application_id='com.endlessm.photos',
                                 flags=Gio.ApplicationFlags.HANDLES_OPEN)

    def do_startup(self):
        """
        Overrides the default Gio.Application.startup handler.

        This code is executed whenever the application starts up; we create the
        main window here.
        """
        # Chaining up is required
        Endless.Application.do_startup(self)

        # Load GResource bundles
        asset_resource = Gio.Resource.load(ASSET_RESOURCE_PATH);
        asset_resource._register();
        thumbnail_resource = Gio.Resource.load(THUMBNAIL_RESOURCE_PATH);
        thumbnail_resource._register();

        credits = Gio.File.new_for_uri('resource://' + BASE_RESOURCE_PREFIX +
            'credits.json')
        self.props.image_attribution_file = credits

        # Style CSS
        provider = Gtk.CssProvider()
        css_file = Gio.File.new_for_uri('resource://' + BASE_RESOURCE_PREFIX + 'endless_photos.css')
        provider.load_from_file(css_file);
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        # Create the mvp for the Photo app and attach the window to the
        # application.
        self._model = PhotosModel()
        self._view = PhotosView(application=self)
        self._presenter = PhotosPresenter(model=self._model, view=self._view)
        self._view.set_presenter(self._presenter)

        self._window = self._view.get_window()
        self.add_window(self._window)
        self._window.show_all()

    def do_open(self, files, nfiles, hint):
        self._presenter.on_open(files[0].get_path());
        self.activate();

    def do_activate(self):
        """
        Overrides the default Gio.Application.activate handler.

        It is required to override this in a subclass of Gio.Application. We
        will just ask the window to present itself whenever this happens, i.e.
        a new image is opened from the file manager.
        """
        self._window.present()
