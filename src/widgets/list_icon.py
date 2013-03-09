from gi.repository import Gtk
from list_button import ListButton

class IconList(Gtk.VBox):

    def __init__(self):
        super(IconList, self).__init__(homogeneous=False, spacing=0)
        self._icons = {}

    def add_icon(self, thumbnail_path, name,  label, clicked_callback):
        option = ListButton(
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


