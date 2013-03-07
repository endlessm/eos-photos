from gi.repository import Gtk, GdkPixbuf, Gdk


class ListButton(Gtk.EventBox):

    def __init__(self, image_path="", name="", label_name="",
                 clicked_callback=None, vertical=False, label_wrap=150):
        super(ListButton, self).__init__(name=name+"-event-box")

        self._clicked_callback = clicked_callback
        self._image = Gtk.Image(name=name+"-image", file=image_path)
        self._label = Gtk.Label(name=name+"-label", label=label_name)
        self._label.set_line_wrap(True)
        self._label.set_size_request(label_wrap, -1)
        table = Gtk.Table(1, 1, False)
        table.attach(self._label, 0, 1, 0, 1, Gtk.AttachOptions.SHRINK | Gtk.AttachOptions.FILL)

        if vertical:
            self._box = Gtk.VBox(homogeneous=False, spacing=0)
        else:
            self._box = Gtk.HBox(homogeneous=False, spacing=0)

        self._box.pack_start(self._image, expand=False, fill=False, padding=0)
        self._box.pack_start(table, expand=False, fill=False, padding=2)

        self.add(self._box)

        self.connect('leave-notify-event', self._on_mouse_leave)
        self.connect('enter-notify-event', self._on_mouse_enter)
        self.connect('button-release-event', self._on_button_release)

    def select(self):
        flags = self._image.get_state_flags() | Gtk.StateFlags.SELECTED
        self._image.set_state_flags(flags, True)
        self._label.set_state_flags(flags, True)

    def deselect(self):
        flags = Gtk.StateFlags(self._image.get_state_flags() & ~Gtk.StateFlags.SELECTED)
        self._image.set_state_flags(flags, True)
        self._label.set_state_flags(flags, True)

    def _on_mouse_enter(self, event, data=None):
        flags = self._image.get_state_flags() | Gtk.StateFlags.PRELIGHT
        self._image.set_state_flags(flags, True)
        self._label.set_state_flags(flags, True)

    def _on_mouse_leave(self, event, data=None):
        flags = Gtk.StateFlags(self._image.get_state_flags() & ~Gtk.StateFlags.PRELIGHT)
        self._image.set_state_flags(flags, True)
        self._label.set_state_flags(flags, True)

    def _on_button_release(self, event, data=None):
        #if mouse is no longer over eventbox, don't select the filter
        if self._image.get_state_flags() & Gtk.StateFlags.PRELIGHT == 0:
            return
        if self._clicked_callback is not None:
            self._clicked_callback()
