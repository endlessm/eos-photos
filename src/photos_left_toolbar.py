import collections
import cairo
from gi.repository import Gtk, Gdk, GdkPixbuf

from widgets.composite_button import CompositeButton
from widgets.image_text_button import ImageTextButton
from resource_prefixes import *


class PhotosLeftToolbar(Gtk.VBox):
    """
    The left filter selection toolbar for the photo app.
    """
    def __init__(self, categories=[], **kw):
        super(PhotosLeftToolbar, self).__init__(homogeneous=False, spacing=0, **kw)
        self._separator_images = {
            "top": GdkPixbuf.Pixbuf.new_from_resource(IMAGES_RESOURCE_PREFIX + "separator_black.png"),
            "bottom": GdkPixbuf.Pixbuf.new_from_resource(IMAGES_RESOURCE_PREFIX + "separator_white.png"),
            "top-shadow": GdkPixbuf.Pixbuf.new_from_resource(IMAGES_RESOURCE_PREFIX + "separator-opened_top-shadow.png"),
            "bottom-shadow": GdkPixbuf.Pixbuf.new_from_resource(IMAGES_RESOURCE_PREFIX + "separator-opened_bottom-shadow.png")
        }

        self._categories = {}
        for category in categories:
            name = category.get_name()
            self._categories[name] = CategoryExpander(self._separator_images, category)
            self.pack_start(self._categories[name], expand=False, fill=True, padding=0)

        self.set_vexpand(True)
        self.show_all()

    def set_presenter(self, presenter):
        self._presenter = presenter

    def change_category(self, category_label):
        # If the user selected a category that isn't Transformations,
        # cancel any in-progress crop that's going on (but retain the
        # current crop dimensions, if any)
        if category_label != "transform" and hasattr(self, '_presenter'):
            # do something to cancel crop
            self._presenter.on_crop_cancel()

        for name, category in self._categories.items():
            if not name == category_label:
                category.unexpand()


class CategoryScrollWindow(Gtk.ScrolledWindow):
    def __init__(self, **kw):
        super(CategoryScrollWindow, self).__init__(**kw)

    def do_get_preferred_height(self):
        children = self.get_children()
         # Always request at least 2 pixels so we can draw the top and bottom separators
        natural_height = min_height = 2
        if children:
            natural_height = max(children[0].get_preferred_height()[1], natural_height)
        return min_height, natural_height


class ScrollWindowDropShadow(Gtk.Widget):
    def __init__(self, separator_images, **kw):
        super(ScrollWindowDropShadow, self).__init__(**kw)
        self._separator_images = separator_images
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
        Gdk.cairo_set_source_pixbuf(cr, self._separator_images["top-shadow"], 0, 0)
        cr.paint()
        Gdk.cairo_set_source_pixbuf(cr, self._separator_images["top"], 0, 0)
        cr.paint()
        Gdk.cairo_set_source_pixbuf(cr, self._separator_images["bottom-shadow"], 0,
                                    alloc.height - self._separator_images["bottom-shadow"].get_height())
        cr.paint()
        Gdk.cairo_set_source_pixbuf(cr, self._separator_images["bottom"], 0,
                                    alloc.height - self._separator_images["bottom"].get_height())
        cr.paint()

class CategoryButton(Gtk.Button, CompositeButton):
    def __init__(self, category_label, **kw):
        super(CategoryButton, self).__init__(**kw)
        self._icon_frame = Gtk.Frame()
        self._icon_frame.get_style_context().add_class("category-image-frame")
        self._icon_frame.set_size_request(21, 21)

        self._icon_align = Gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0.0, yscale=0.0)
        self._icon_align.add(self._icon_frame)

        self._category_label = Gtk.Label(label=category_label, name="category-label")
        self._category_label.get_style_context().add_class("label")

        self._arrow_frame = Gtk.Frame(halign=Gtk.Align.END)
        self._arrow_frame.get_style_context().add_class("arrow-frame")
        self._arrow_frame.set_size_request(21, 21)
        self._arrow_align = Gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0.0, yscale=0.0)
        self._arrow_align.add(self._arrow_frame)

        self._hbox = Gtk.HBox(homogeneous=False, spacing=0, margin_top=8, margin_bottom=8)
        self._hbox.pack_start(self._arrow_align, expand=False, fill=False, padding=0)
        self._hbox.pack_start(self._icon_align, expand=False, fill=False, padding=2)
        self._hbox.pack_start(self._category_label, expand=False, fill=False, padding=10)
        # This hackish line keeps the expander widget from downsizing
        # horizontally after the separator is removed. 183 is the width of the
        # separator image
        self._hbox.set_size_request(183, -1)

        self.add(self._hbox)
        self.set_sensitive_children([self._category_label, self._icon_frame, self._arrow_frame])

class CategoryExpander(Gtk.Grid):
    def __init__(self, separator_images, widget, **kw):
        kw["name"] = widget.get_name() + "-expander"
        kw["orientation"] = Gtk.Orientation.VERTICAL
        super(CategoryExpander, self).__init__(**kw)
        self.get_style_context().add_class("category-expander")

        self._button = CategoryButton(widget.get_label())

        self._widget = widget
        self._revealer = Gtk.Revealer()
        self._revealer.add(self._widget)
        self._scroll_area = CategoryScrollWindow()
        self._scroll_area.get_style_context().add_class("filters-scroll-area")
        self._scroll_area.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self._scroll_area.add_with_viewport(self._revealer)
        self._scroll_area.connect("size-allocate", self._update_scroll)
        self._drop_shadow = ScrollWindowDropShadow(separator_images)
        self._overlay = Gtk.Overlay()
        self._overlay.add(self._scroll_area)
        self._overlay.add_overlay(self._drop_shadow)

        self.add(self._button)
        self.add(self._overlay)
        self._expanded = False
        self._button.connect("clicked", lambda (w): self._toggle_expanded())
        self._scroll_target = 0

    def _update_scroll(self, w, a):
        if not self._revealer.get_child_revealed():
            self._scroll_area.get_vadjustment().set_value(self._scroll_target)

    def _toggle_expanded(self):
        if self._expanded:
            self.unexpand()
        else:
            self.expand()

    def expand(self):
        try:
            self._scroll_target = self._widget.get_desired_scroll_position()
        except NotImplementedError:
            self._scroll_target = 0
        self.get_parent().change_category(self._widget.get_name())
        self.get_style_context().add_class("expanded")
        self._revealer.set_reveal_child(True)
        self._expanded = True

    def unexpand(self):
        self.get_style_context().remove_class("expanded")
        self._revealer.set_reveal_child(False)
        self._expanded = False
