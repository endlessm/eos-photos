from gi.repository import Gtk


prelight = Gtk.StateFlags.PRELIGHT
active = Gtk.StateFlags.ACTIVE


class CompositeButton(object):
    _handler_set = False


    def set_sensitive_children(self, children):
        # Set the list of child widgets which will inherit the CompositeButton's
        # hover/active state flags.
        self.sensitive_children = children

        # If the handlers for mouse events aren't already set, conenct them
        if not self._handler_set:
            self._connect_meta_handler()


    def _connect_meta_handler(self):
        self.connect('enter-notify-event', self._meta_handler(prelight, True))
        self.connect('leave-notify-event', self._meta_handler(prelight, False))
        self.connect('button-press-event', self._meta_handler(active, True))
        self.connect('button-release-event', self._meta_handler(active, False))

        self._handler_set = True


    def _meta_handler(self, event_flag, set_value): 
        # Return an event handler which does nothing but set the value of
        # the event_flag to set_value on all sensitive children
        def event_handler(*args):
            for child in self.sensitive_children:
                if set_value:
                    flags = child.get_state_flags() | event_flag
                    child.set_state_flags(event_flag, True)
                else:
                    child.unset_state_flags(Gtk.StateFlags.PRELIGHT)

        return event_handler
