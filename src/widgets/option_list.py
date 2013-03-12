from gi.repository import Gtk


class OptionLabel(Gtk.Label):
    def __init__(self, image=None, **kw):
        super(OptionLabel, self).__init__(**kw)
        self._image = image
        self.set_justify(Gtk.Justification.CENTER)

    def do_get_preferred_width(self):
        if self._image is not None:
            return self._image.get_preferred_width()
        return Gtk.Label.do_get_preferred_width()


class Option(Gtk.EventBox):

    def __init__(self, image_path="", name="", label_name="",
                 clicked_callback=None, vertical=False, label_wrap=150):
        super(Option, self).__init__(name=name+"-event-box")

        self._clicked_callback = clicked_callback
        self._image = Gtk.Image(name=name+"-image", file=image_path)
        self._label = OptionLabel(image=self._image, name=name+"-label", label=label_name)
        # self._label = Gtk.Label(name=name+"-label", label=label_name)
        self._label.set_line_wrap(True)
        # table = Gtk.Table(1, 1, False)
        # table.attach(self._label, 0, 1, 0, 1, Gtk.AttachOptions.SHRINK | Gtk.AttachOptions.FILL)

        if vertical:
            self._box = Gtk.VBox(homogeneous=False, spacing=0)
        else:
            self._box = Gtk.HBox(homogeneous=False, spacing=0)

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

    def __init__(self):
        super(OptionList, self).__init__(homogeneous=False, spacing=0)
        self._icons = {}

    def add_icon(self, thumbnail_path, name,  label, clicked_callback):
        option = Option(
            image_path=thumbnail_path, name=name, label_name=label,
            clicked_callback=clicked_callback,
            vertical=True)
        self._icons[label] = option
        self.pack_start(option, expand=False, fill=False, padding=0)
        self.show_all()

    def select_icon(self, label_name):
        for name, icon in self._icons.items():
            if name == label_name:
                icon.select()
            else:
                icon.deselect()
