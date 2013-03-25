import collections

from gi.repository import Gtk
from widgets.option_list import OptionList


class PhotosLeftToolbar(Gtk.VBox):
    """
    The left filter selection toolbar for the photo app.
    """
    def __init__(self, images_path="", adjustments=None, borders=None, filters=None, **kw):
        super(PhotosLeftToolbar, self).__init__(homogeneous=False, spacing=0, **kw)
        self._images_path = images_path

        self._categories = collections.OrderedDict()

        filter_align = Gtk.Alignment(xalign=0.0, yalign=0.0, xscale=0.0, yscale=0.0, left_padding=30)
        filter_align.add(filters)
        self._categories["filters"] = Category(filter_align,
            images_path=self._images_path, label=_("FILTERS"),
            expanded_callback=lambda: self.change_category("filters"))

        adjustments_align = Gtk.Alignment(xalign=0.0, yalign=0.0, xscale=1.0, yscale=0.0, left_padding=15)
        adjustments_align.add(adjustments)
        self._categories["adjustments"] = Category(adjustments_align, 
            images_path=self._images_path, label=_("ADJUSTMENTS"),
            expanded_callback=lambda: self.change_category("adjustments"))

        border_align = Gtk.Alignment(xalign=0.0, yalign=0.0, xscale=0.0, yscale=0.0, left_padding=30)
        border_align.add(borders)
        self._categories["borders"] = Category(border_align,
            images_path=self._images_path, label=_("BORDERS"),
            expanded_callback=lambda: self.change_category("borders"))

        for category in self._categories.values():
            self.pack_start(category, expand=False, fill=True, padding=20)

        self.set_vexpand(True)
        self.show_all()

    def set_presenter(self, presenter):
        self._presenter = presenter

    def change_category(self, category_name):
        for name, category in self._categories.items():
            if not name == category_name:
                category.deselect()


class CatagoryScrollWindow(Gtk.ScrolledWindow):
    def __init__(self, **kw):
        super(CatagoryScrollWindow, self).__init__(**kw)

    def do_get_preferred_height(self):
        children = self.get_children()
        min_height = Gtk.ScrolledWindow.do_get_preferred_height(self)[0]
        natural_height = min_height
        if children:
            natural_height = max(children[0].get_preferred_height()[1], natural_height)
        return min_height, natural_height


class Category(Gtk.Expander):
    def __init__(self, widget, images_path="", label="", expanded_callback=None, **kw):
        super(Category, self).__init__(**kw)

        self._expanded_callback = expanded_callback
        self._images_path = images_path
        self._title_image = Gtk.Image.new_from_file(images_path + "Filter-icon.png")
        self._title_label = Gtk.Label(label=label, name="filters-title")
        self._title_box = Gtk.HBox(homogeneous=False, spacing=0)
        self._title_box.pack_start(self._title_image, expand=False, fill=False, padding=0)
        self._title_box.pack_start(self._title_label, expand=False, fill=False, padding=2)
        self.set_label_widget(self._title_box)
        #self._title_allign = Gtk.HBox(homogeneous=False, spacing=0)
        #self._title_allign.pack_start(borders_title_box, expand=False, fill=False, padding=10)

        self._widget = widget
        self._scroll_area = CatagoryScrollWindow(name="filters-scroll-area")
        self._scroll_area.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self._scroll_area.add_with_viewport(self._widget)

        # self._separator = Gtk.Separator.new(Gtk.Orientation.HORIZONTAL)
        # self.add(self._separator)

        # self._drop_shadow = Gtk.Image.new_from_file(images_path + "Filter-mask-shadow.png")
        # self._drop_shadow.set_halign(Gtk.Align.CENTER)
        # self._drop_shadow.set_valign(Gtk.Align.START)
        # self._overlay = Gtk.Overlay()
        # self._overlay.add(self._scroll_area)
        # self._overlay.add_overlay(self._drop_shadow)

        self.connect('notify::expanded', self.expanded_cb)
        self.set_resize_toplevel(True)

    def expanded_cb(self, widget, event):
        if self.get_expanded():
            # self._title_box.select()
            self.add(self._scroll_area)
            self._expanded_callback()
        else:
            self.remove(self._scroll_area)
            # self._title_box.deselect()
        self.show_all()

    def get_widget(self):
        return self._widget

    def select(self):
        self.set_expanded(True)

    def deselect(self):
        self.set_expanded(False)

    def is_selected(self):
        return self.get_expanded()
