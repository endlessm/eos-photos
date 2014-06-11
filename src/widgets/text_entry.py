from gi.repository import Gtk, Gdk


class TextEntry(Gtk.Frame):
    __gtype_name__ = 'TextEntry'
    DEFAULT_HEIGHT = 90
    """
    A TextView with convenience methods that mirror TextEntry, but with a
    multiline text editor. Includes default help text that disappears on selection.

    This could be made into a utility class, but it would probably need to be
    converted to Javascript.
    """
    def __init__(self, default_text, **kw):
        super(TextEntry, self).__init__(**kw)

        self._text_view = Gtk.TextView()
        self._text_view.set_wrap_mode(Gtk.WrapMode.WORD)
        self._text_view.set_hexpand(False)
        # This is essentially padding, not border
        self._text_view.set_border_width(5)

        self._scroll = Gtk.ScrolledWindow()
        self._scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self._scroll.add(self._text_view)

        self.add(self._scroll)
        self.set_size_request(-1, TextEntry.DEFAULT_HEIGHT)
        self.set_hexpand(True)

        self._default_text = default_text

        grey_color = Gdk.RGBA(red=0, green=0, blue=0, alpha=.5)
        # Style for default help text
        self.get_buffer().create_tag('default', editable=False, foreground_rgba=grey_color)

        self._text_view.connect('focus-in-event', self._focus_callback)
        self._text_view.connect_after('focus-out-event', self._lose_focus_callback)
        self._show_default_text()

    # Gets the start and end iters for the buffer. Iters only last until the
    # text changes
    def _get_buffer_iters(self):
        startIter = self.get_buffer().get_start_iter()
        endIter = self.get_buffer().get_end_iter()
        return (startIter, endIter)

    def get_default_text(self):
        return self._default_text

    # Returns the text entered, or "" if the default text is showing
    def get_text(self):
        text = ""
        if not self._default_text_displayed:
            iters = self._get_buffer_iters()
            text = self.get_buffer().get_text(iters[0], iters[1], False)
        return text

    def get_buffer(self):
        return self._text_view.get_buffer()

    def _show_default_text(self):
        self._text_view.set_cursor_visible(False)
        self._default_text_displayed = True
        self.get_buffer().set_text(self._default_text)
        iters = self._get_buffer_iters()

        self.get_buffer().apply_tag_by_name('default', iters[0], iters[1])

    def _remove_default_text(self):
        self._default_text_displayed = False
        self.get_buffer().set_text("")
        self._text_view.set_cursor_visible(True)

    # Removes the default text when the focus is gained if the default text is
    # currently being displayed
    def _focus_callback(self, thing, otherThing):
        if self._default_text_displayed:
            self._remove_default_text()
        return False

    # Shows the default text when the focus is lost, as long as there is no
    # other text entered
    def _lose_focus_callback(self, thing, otherThing):
        if not self._default_text_displayed and len(self.get_text()) == 0:
            self._show_default_text()
        return False
