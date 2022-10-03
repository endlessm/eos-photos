import os
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf


class PreviewFileChooserDialog(Gtk.FileChooserDialog):
    PREVIEW_MAX_SIZE = 128
    def __init__(self, **kw):
        super(PreviewFileChooserDialog, self).__init__(**kw)

        self._preview = Gtk.Image()
        # Don't let preview size down horizontally for skinny images, cause
        # that looks distracting
        self._preview.set_size_request(PreviewFileChooserDialog.PREVIEW_MAX_SIZE, -1)
        self.set_preview_widget(self._preview)
        self.set_use_preview_label(False)
        self.connect("update-preview", self.update_preview_cb)

    def update_preview_cb(self, file_chooser):
        filename = self.get_preview_filename()
        if filename is None or os.path.isdir(filename):
            self.set_preview_widget_active(False)
            return
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(filename,
                PreviewFileChooserDialog.PREVIEW_MAX_SIZE,
                PreviewFileChooserDialog.PREVIEW_MAX_SIZE)
            self._preview.set_from_pixbuf(pixbuf)
        except Exception as e:
            print(e)
            self.set_preview_widget_active(False)
            return
        self.set_preview_widget_active(True)
