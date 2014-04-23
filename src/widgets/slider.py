from gi.repository import Gtk, Gdk

class Slider(Gtk.HScale):
    
    SNAP_MARGIN = 0.1

    def __init__(self, adjustment=None, **kw):
        kw.setdefault('draw_value', False)
        kw["adjustment"] = adjustment
        super(Slider, self).__init__(**kw)

        self._reset_to_default = False
        self.DEFAULT_VALUE = adjustment.get_value()

        self.connect('button-press-event', self._detect_double_click)
    
    # Override default button-release event, so when
    # user releases the mouse after a double click, the
    # value is set to the default value rather than
    # the current cursor position
    def do_button_release_event(self, event):
        Gtk.HScale.do_button_release_event(self, event)
        if self._reset_to_default:
            self._reset_to_default = False
            self.set_value(self.DEFAULT_VALUE)

    def do_value_changed(self, **kw):
        current_val = self.get_adjustment().get_value() 
        dist_to_default = abs(current_val - self.DEFAULT_VALUE)
        if dist_to_default < self.SNAP_MARGIN:
            self.set_value(self.DEFAULT_VALUE)
        return True

    # If the user just double-clicked, set the flag to true
    # so the release handler knows to reset to default
    def _detect_double_click(self, window, event):
        if event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
            self._reset_to_default = True
            return True
