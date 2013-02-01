from gi.repository import Gtk

class PhotosLeftToolbar(Gtk.VBox):
    """
    The left filter selection toolbar for the photo app.
    """
    def __init__(self, **kw):
        super(PhotosLeftToolbar, self).__init__(homogeneous=False, spacing=0, **kw)
        
        filters_image = Gtk.Image.new_from_file("../images/Filters_title.png")
        filters_label = Gtk.Label("FILTROS")
        filters_title_box = Gtk.HBox(homogeneous=False, spacing=0)
        filters_title_box.pack_start(filters_image, expand=False, fill=False, padding=0)
        filters_title_box.pack_start(filters_label, expand=False, fill=False, padding=2)
        filters_title_allign = Gtk.Alignment(xalign=0.5, yalign=0.0, xscale=0.0, yscale=0.0)
        filters_title_allign.add(filters_title_box)

        scroll_contents = Gtk.VBox(homogeneous=False, spacing=8)
        scroll_contents.pack_start(FilterOption(), expand=False, fill=False, padding=0)
        scroll_contents.pack_start(FilterOption(), expand=False, fill=False, padding=0)
        scroll_contents.pack_start(FilterOption(), expand=False, fill=False, padding=0)
        scroll_contents.pack_start(FilterOption(), expand=False, fill=False, padding=0)
        scroll_contents.pack_start(FilterOption(), expand=False, fill=False, padding=0)
        scroll_contents.pack_start(FilterOption(), expand=False, fill=False, padding=0)
        scroll_contents.pack_start(FilterOption(), expand=False, fill=False, padding=0)
        scroll_contents.pack_start(FilterOption(), expand=False, fill=False, padding=0)
        scroll_contents.pack_start(FilterOption(), expand=False, fill=False, padding=0)


        scroll_area = Gtk.ScrolledWindow(name="filters-scroll-area")
        scroll_area.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll_area.add_with_viewport(scroll_contents)

        drop_shadow = Gtk.Image.new_from_file("../images/Filters_drop-shadow.png")
        drop_shadow.set_halign(Gtk.Align.CENTER)
        drop_shadow.set_valign(Gtk.Align.START)
        overlay = Gtk.Overlay()
        overlay.add(scroll_area)
        overlay.add_overlay(drop_shadow)

        self.pack_start(filters_title_allign, expand=False, fill=False, padding=20)
        self.pack_start(overlay, expand=True, fill=True, padding=0)

    def set_presenter(self, presenter):
        self._presenter = presenter

class FilterOption(Gtk.Alignment):
    """
    A selectable filter option with an image and caption.
    """
    def __init__(self):
        super(FilterOption, self).__init__(xalign=0.5, yalign=0.0, xscale=0.0, yscale=0.0)
        option_image = Gtk.Image.new_from_file("../images/Filters_Example-Picture_01.jpg")
        option_label = Gtk.Label("NORMAL")

        vbox = Gtk.VBox(homogeneous=False, spacing=0)
        vbox.pack_start(option_image, expand=False, fill=False, padding=0)
        vbox.pack_start(option_label, expand=False, fill=False, padding=2)
        self.add(vbox)
