from gi.repository import Gtk


class OptionLabel(Gtk.Label):
    """
    Label for a list option.
    """
    def __init__(self, image=None, **kw):
        super(OptionLabel, self).__init__(**kw)
        self._image = image
        self.set_justify(Gtk.Justification.CENTER)

    def do_get_preferred_width(self):
        if self._image is not None:
            return self._image.get_preferred_width()
        return Gtk.Label.do_get_preferred_width()


class Option(Gtk.EventBox):
    """
    Options for the OptionList, these widgets display a thumbnail and a label
    fit underneath.
    """
    def __init__(self, name="", image_path="", label="", clicked_callback=None):
        super(Option, self).__init__(name=name+"-event-box")

        self._clicked_callback = clicked_callback
        self._image = Gtk.Image(name=name+"-image", file=image_path)
        self._label = OptionLabel(image=self._image, name=name+"-label", label=label)
        self._label.set_line_wrap(True)

        self._box = Gtk.VBox(homogeneous=False, spacing=0)

        self._box.pack_start(self._image, expand=False, fill=False, padding=0)
        self._box.pack_start(self._label, expand=True, fill=True, padding=0)

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


class OptionList(Gtk.VBox):
    """
    A list of clickable options packed vertically.

    Add Options to this list. They will not select themselves automatically,
    but call the clicked_callback instead.
    """
    def __init__(self):
        super(OptionList, self).__init__(homogeneous=False, spacing=0)
        self._icons = {}

    def add_option(self, name, thumbnail_path, label, clicked_callback):
        option = Option(
            name=name, image_path=thumbnail_path, label=label,
            clicked_callback=clicked_callback)
        self._icons[label] = option
        self.pack_start(option, expand=False, fill=False, padding=0)

    def select_option(self, label_name):
        for name, icon in self._icons.items():
            if name == label_name:
                icon.select()
            else:
                icon.deselect()
