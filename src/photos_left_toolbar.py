import collections
import cairo
from gi.repository import Gtk, Gdk, GdkPixbuf

from widgets.toolbar_separator import ToolbarSeparator
from widgets.image_text_button import ImageTextButton


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

        self._revert_button = ImageTextButton(label=_("REVERT TO ORIGINAL"),
                                              name="revert-button")
        self._revert_button.connect("clicked", lambda e: self._presenter.on_revert())
        self.pack_end(self._revert_button, expand=False, fill=False, padding=0)
        self._separator = ToolbarSeparator(images_path=images_path)
        self.pack_end(self._separator, expand=False, fill=False, padding=0)
        self._removed_separator = False

        self.set_vexpand(True)
        self.show_all()
        self.connect('size-allocate', self._check_full)

    def set_presenter(self, presenter):
        self._presenter = presenter

    def change_category(self, category_label):
        for label, category in self._categories.items():
            if not label == category_label:
                category.deselect()

    def _check_full(self, w, alloc):
        if alloc.height <= self.get_preferred_height()[1]:
            if not self._removed_separator:
                self._removed_separator = True
                self._separator.hide()
                # self.remove(self._separator)
        elif self._removed_separator:
            self._removed_separator = False
            self._separator.show()
            # self.pack_end(self._separator, expand=False, fill=False, padding=0)


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
        kw["name"] = widget.get_name() + "-expander"
        super(CategoryExpander, self).__init__(**kw)
        self.get_style_context().add_class("category-expander")

        self._icon_frame = Gtk.Frame()
        self._icon_frame.get_style_context().add_class("image-frame")
        self._icon_frame.set_size_request(21, 21)

        self._icon_align = Gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0.0, yscale=0.0)
        self._icon_align.add(self._icon_frame)

        self._category_label = Gtk.Label(label=widget.get_label(), name="category-label")
        self._category_label.get_style_context().add_class("category-label")

        self._hbox = Gtk.HBox(homogeneous=False, spacing=0)
        self._hbox.pack_start(self._icon_align, expand=False, fill=False, padding=9)
        self._hbox.pack_start(self._category_label, expand=False, fill=False, padding=0)

        self._arrow_frame = Gtk.Frame()
        self._arrow_frame.get_style_context().add_class("arrow-frame")
        self._arrow_frame.set_size_request(21, 21)
        self._arrow_align = Gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0.0, yscale=0.0)
        self._arrow_align.add(self._arrow_frame)
        self._hbox.pack_end(self._arrow_align, expand=False, fill=False, padding=8)

        self._separator = ToolbarSeparator(images_path=images_path, margin_left=0, halign=0)
        self._vbox = Gtk.VBox(homogeneous=False, spacing=0)
        self._vbox.pack_start(self._hbox, expand=False, fill=False, padding=8)
        self._vbox.pack_start(self._separator, expand=False, fill=False, padding=0)
        # This hackish line keeps the expander widget from downsizing
        # horizontally after the separator is removed.
        self._vbox.connect("size-allocate", lambda w, alloc: self._vbox.set_size_request(alloc.width, -1))
        self.set_label_widget(self._vbox)

        self._widget = widget
        self._scroll_area = CategoryScrollWindow()
        self._scroll_area.get_style_context().add_class("filters-scroll-area")
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
            self.get_parent().change_category(self._widget.get_label())
            flags = self._arrow_frame.get_state_flags() | Gtk.StateFlags.ACTIVE
            self._arrow_frame.set_state_flags(flags, True)
        else:
            self._vbox.pack_start(self._separator, expand=False, fill=False, padding=0)
            flags = Gtk.StateFlags(self._arrow_frame.get_state_flags() & ~Gtk.StateFlags.ACTIVE)
            self._arrow_frame.set_state_flags(flags, True)
        self.show_all()

    def _on_mouse_enter(self, widget, event):
        flags = self._arrow_frame.get_state_flags() | Gtk.StateFlags.PRELIGHT
        if self.get_expanded():
            flags = flags | Gtk.StateFlags.ACTIVE
        self._arrow_frame.set_state_flags(flags, True)

    def _on_mouse_leave(self, widget, event):
        flags = Gtk.StateFlags(self._arrow_frame.get_state_flags() & ~Gtk.StateFlags.PRELIGHT)
        if self.get_expanded():
            flags = Gtk.StateFlags(flags & ~Gtk.StateFlags.ACTIVE)
        self._arrow_frame.set_state_flags(flags, True)

    def get_widget(self):
        return self._widget

    def select(self):
        self.set_expanded(True)

    def deselect(self):
        self.set_expanded(False)

    def is_selected(self):
        return self.get_expanded()
