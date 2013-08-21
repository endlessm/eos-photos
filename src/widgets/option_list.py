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
        return Gtk.Label.do_get_preferred_width(self)

    def do_get_preferred_height(self):
        if self._image is not None:
            return Gtk.Label.do_get_preferred_height_for_width(self, self._image.get_preferred_width()[0])
        return Gtk.Label.do_get_preferred_height_for_width(self)



class Option(Gtk.Button):
    """
    Options for the OptionList, these widgets display a thumbnail and a label
    fit underneath.
    """
    def __init__(self, image_path="", label="", clicked_callback=None):
        super(Option, self).__init__()
        self.get_style_context().add_class("option-button")

        self._clicked_callback = clicked_callback
        self._image = Gtk.Image(file=image_path)
        self._image.get_style_context().add_class("option-image")
        self._label = OptionLabel(image=self._image, label=label)
        self._label.get_style_context().add_class("option-label")
        self._label.set_line_wrap(True)

        self._vbox = Gtk.VBox(homogeneous=False, spacing=0)
        self._vbox.pack_start(self._image, expand=False, fill=False, padding=0)
        self._vbox.pack_start(self._label, expand=True, fill=True, padding=0)

        self.add(self._vbox)
        self.connect('clicked', self._on_click)

    def select(self):
        flags = self.get_state_flags() | Gtk.StateFlags.SELECTED
        self.set_state_flags(flags, True)

    def deselect(self):
        flags = Gtk.StateFlags(self.get_state_flags() & ~Gtk.StateFlags.SELECTED)
        self.set_state_flags(flags, True)

    def _on_click(self, event, data=None):
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

    def add_option(self, thumbnail_path, label, clicked_callback):
        option = Option(
            image_path=thumbnail_path, label=label,
            clicked_callback=clicked_callback)
        self._icons[label] = option
        self.pack_start(option, expand=False, fill=False, padding=3)

    def select_option(self, label_name):
        for name, icon in self._icons.items():
            if name == label_name:
                icon.select()
            else:
                icon.deselect()
