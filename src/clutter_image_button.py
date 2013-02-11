from gi.repository import Clutter

class ClutterImageButton(Clutter.Group):
    """
    A simple clutter button with a normal, hover and down state set from three images.
    """
    def __init__(self, normal_path=None, hover_path=None, down_path=None, **kw):
        super(ClutterImageButton, self).__init__(**kw)
        self._normal_texture = Clutter.Texture.new_from_file(normal_path)
        self._hover_texture = Clutter.Texture.new_from_file(hover_path)
        self._down_texture = Clutter.Texture.new_from_file(down_path)

        self.add_child(self._normal_texture)
        self.set_reactive(True)
        self._click_action = Clutter.ClickAction()
        self.add_action(self._click_action)

        self.connect('enter-event', self._on_mouse_enter)
        self.connect('leave-event', self._on_mouse_leave)
        self.connect('button-press-event', self._on_button_press)
        self.connect('button-release-event', self._on_button_release)

    def get_click_action(self):
        return self._click_action

    def _on_mouse_enter(self, event, data=None):
        self.remove_all()
        self.add_child(self._hover_texture)
        return False  # don't block event

    def _on_mouse_leave(self, event, data=None):
        self.remove_all()
        self.add_child(self._normal_texture)
        return False  # don't block event

    def _on_button_press(self, event, data=None):
        self.remove_all()
        self.add_child(self._down_texture)
        return False

    def _on_button_release(self, event, data=None):
        self.remove_all()
        self.add_child(self._hover_texture)
        return False
