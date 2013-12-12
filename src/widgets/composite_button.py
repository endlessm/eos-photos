from gi.repository import Gtk


PRELIGHT = Gtk.StateFlags.PRELIGHT
ACTIVE = Gtk.StateFlags.ACTIVE


class CompositeButton(object):
    # Class mixin for widgets whose :hover and :active CSS pseudoclass states should be
    # inherited by other widgets, since as of GTK 3.10 these flags no longer propagate
    # from a widget to its children. Widgets in sensitive_children will listen to this widget's
    # state-flags-changed event and inherit all flag values listed in inherited_flags


    _handler_set = False
    inherited_flags = [PRELIGHT, ACTIVE]


    def set_sensitive_children(self, children):
        # Set the list of child widgets which will inherit the CompositeButton's
        # hover/active state flags.
        self.sensitive_children = children

        # If the handlers for mouse events aren't already set, conenct them
        if not self._handler_set:
            self._connect_state_changed_handler()


    def _connect_state_changed_handler(self):
        self.connect('state-flags-changed', self._state_changed_handler)

        self._handler_set = True


    def _state_changed_handler(self, widget, prev_flags): 
        my_flags = self.get_state_flags()
        for child in self.sensitive_children:
            for flag in self.inherited_flags:
                # for each flag we want the children to inherit, grab this widget's flag
                # value, and set the child's matching flag accordingly
                my_flag = int(my_flags & flag)
                set_value = (my_flag is not 0)
                if set_value:
                    child.set_state_flags(flag, True)
                else:
                    child.unset_state_flags(flag)
