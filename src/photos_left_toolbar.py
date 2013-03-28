import collections
import cairo
from gi.repository import Gtk, Gdk, GdkPixbuf

from widgets.toolbar_separator import ToolbarSeparator


class PhotosLeftToolbar(Gtk.VBox):
    """
    The left filter selection toolbar for the photo app.
    """
    def __init__(self, images_path="", categories=[], **kw):
        super(PhotosLeftToolbar, self).__init__(homogeneous=False, spacing=0, **kw)
        self._images_path = images_path

        self._categories = {}
        for category in categories:
            label = category.get_label()
            self._categories[label] = CategoryExpander(images_path, category)
            self.pack_start(self._categories[label], expand=False, fill=True, padding=0)

        self.set_vexpand(True)
        self.show_all()

    def set_presenter(self, presenter):
        self._presenter = presenter

    def change_category(self, category_label):
        for label, category in self._categories.items():
            if not label == category_label:
                category.deselect()


class CategoryScrollWindow(Gtk.ScrolledWindow):
    def __init__(self, images_path="", **kw):
        super(CategoryScrollWindow, self).__init__(**kw)

    def do_get_preferred_height(self):
        children = self.get_children()
        min_height = Gtk.ScrolledWindow.do_get_preferred_height(self)[0]
        natural_height = min_height
        if children:
            natural_height = max(children[0].get_preferred_height()[1], natural_height)
        return min_height, natural_height


class ScrollWindowDropShadow(Gtk.Widget):
    def __init__(self, images_path="", **kw):
        super(ScrollWindowDropShadow, self).__init__(**kw)
        self._top_shadow = GdkPixbuf.Pixbuf.new_from_file(images_path + "separator-opened_top-shadow.png")
        self._top_separator = GdkPixbuf.Pixbuf.new_from_file(images_path + "separator_black.png")
        self._bottom_shadow = GdkPixbuf.Pixbuf.new_from_file(images_path + "separator-opened_bottom-shadow.png")
        self._bottom_separator = GdkPixbuf.Pixbuf.new_from_file(images_path + "separator_white.png")
        self.set_has_window(False)
        self.set_app_paintable(True)
        self.connect('draw', self._draw)
        self.connect_after('realize', self._realize)

    def _realize(self, w):
        # Big old hack to keep from getting input in this widget. Sets the Gdk
        # input region to be none so events will propagate down.
        # set_child_input_shapes set this widget to have the input region of
        # its children and since it has no children this is an empty area.
        # Other input region methods are not introspectable.
        window = self.get_window()
        window.set_child_input_shapes()

    def _draw(self, w, cr):
        alloc = self.get_allocation()
        Gdk.cairo_set_source_pixbuf(cr, self._top_shadow, 0, 0)
        cr.paint()
        Gdk.cairo_set_source_pixbuf(cr, self._top_separator, 0, 0)
        cr.paint()
        Gdk.cairo_set_source_pixbuf(cr, self._bottom_shadow, 0, alloc.height - self._bottom_shadow.get_height())
        cr.paint()
        Gdk.cairo_set_source_pixbuf(cr, self._bottom_separator, 0, alloc.height - self._bottom_separator.get_height())
        cr.paint()
        return True


class CategoryExpander(Gtk.Expander):
    def __init__(self, images_path, widget, **kw):
        super(CategoryExpander, self).__init__(**kw)

        self._images_path = images_path
        self._normal_icon_pixbuf = GdkPixbuf.Pixbuf.new_from_file(images_path + widget.get_normal_icon_path())
        self._hover_icon_pixbuf = GdkPixbuf.Pixbuf.new_from_file(images_path + widget.get_hover_icon_path())

        self._category_icon = Gtk.Image.new_from_pixbuf(self._normal_icon_pixbuf)
        self._category_label = Gtk.Label(label=widget.get_label(), name="category-label")
        self._hbox = Gtk.HBox(homogeneous=False, spacing=0)
        self._hbox.pack_start(self._category_icon, expand=False, fill=False, padding=9)
        self._hbox.pack_start(self._category_label, expand=False, fill=False, padding=0)

        self._up_pixbuf = GdkPixbuf.Pixbuf.new_from_file(images_path + "icon_arrow-up.png")
        self._down_pixbuf = GdkPixbuf.Pixbuf.new_from_file(images_path + "icon_arrow-down.png")
        self._arrow = Gtk.Image.new_from_pixbuf(self._down_pixbuf)

        self._separator = ToolbarSeparator(images_path=images_path, margin_left=0, halign=0)
        self._vbox = Gtk.VBox(homogeneous=False, spacing=0)
        self._vbox.pack_start(self._hbox, expand=False, fill=False, padding=8)
        self._vbox.pack_start(self._separator, expand=False, fill=False, padding=0)
        # This hackish line keeps the expander widget from downsizing
        # horizontally after the separator is removed.
        self._vbox.connect("size-allocate", lambda w, alloc: self._vbox.set_size_request(alloc.width, -1))
        self.set_label_widget(self._vbox)

        self._widget = widget
        self._scroll_area = CategoryScrollWindow(name="filters-scroll-area")
        self._scroll_area.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self._scroll_area.add_with_viewport(self._widget)
        self._drop_shadow = ScrollWindowDropShadow(images_path=images_path)
        self._overlay = Gtk.Overlay()
        self._overlay.add(self._scroll_area)
        self._overlay.add_overlay(self._drop_shadow)
        self.add(self._overlay)

        self.connect('notify::expanded', self._on_expanded)
        self.connect('enter-notify-event', self._on_mouse_enter)
        self.connect('leave-notify-event', self._on_mouse_leave)

    def _on_expanded(self, widget, event):
        if self.get_expanded():
            self._vbox.remove(self._separator)
            self._arrow.set_from_pixbuf(self._up_pixbuf)
            self.get_parent().change_category(self._widget.get_label())
        else:
            self._vbox.pack_start(self._separator, expand=False, fill=False, padding=0)
            self._arrow.set_from_pixbuf(self._down_pixbuf)
        self.show_all()

    def _on_mouse_enter(self, widget, event):
        self._category_icon.set_from_pixbuf(self._hover_icon_pixbuf)
        # flags = self._category_label.get_state_flags() | Gtk.StateFlags.PRELIGHT
        # self._category_label.set_state_flags(flags)
        self._hbox.pack_end(self._arrow, expand=False, fill=False, padding=8)
        self.show_all()

    def _on_mouse_leave(self, widget, event):
        self._category_icon.set_from_pixbuf(self._normal_icon_pixbuf)
        # flags = Gtk.StateFlags(self._category_label.get_state_flags() & ~Gtk.StateFlags.PRELIGHT)
        # self._category_label.set_state_flags(flags)
        self._hbox.remove(self._arrow)
        self.show_all()

    def get_widget(self):
        return self._widget

    def select(self):
        self.set_expanded(True)

    def deselect(self):
        self.set_expanded(False)

    def is_selected(self):
        return self.get_expanded()
