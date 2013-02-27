from gi.repository import Gtk

class PhotosLeftToolbar(Gtk.VBox):
    """
    The left filter selection toolbar for the photo app.
    """
    def __init__(self, images_path="", **kw):
        super(PhotosLeftToolbar, self).__init__(homogeneous=False, spacing=0, **kw)
        self._images_path = images_path

        self._filters_image = Gtk.Image.new_from_file(images_path + "Filters_title.png")
        self._filters_label = Gtk.Label("FILTROS")
        self._filters_title_box = Gtk.HBox(homogeneous=False, spacing=0)
        self._filters_title_box.pack_start(self._filters_image, expand=False, fill=False, padding=0)
        self._filters_title_box.pack_start(self._filters_label, expand=False, fill=False, padding=2)
        self._filters_title_allign = Gtk.Alignment(xalign=0.5, yalign=0.0, xscale=0.0, yscale=0.0)
        self._filters_title_allign.add(self._filters_title_box)

        self._scroll_contents = Gtk.VBox(homogeneous=False, spacing=8)
        self._filter_options = {}

        self._scroll_area = Gtk.ScrolledWindow(name="filters-scroll-area")
        self._scroll_area.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self._scroll_area.add_with_viewport(self._scroll_contents)

        self._drop_shadow = Gtk.Image.new_from_file(images_path + "Filters_drop-shadow.png")
        self._drop_shadow.set_halign(Gtk.Align.CENTER)
        self._drop_shadow.set_valign(Gtk.Align.START)
        self._overlay = Gtk.Overlay()
        self._overlay.add(self._scroll_area)
        self._overlay.add_overlay(self._drop_shadow)

        self.pack_start(self._filters_title_allign, expand=False, fill=False, padding=20)
        self.pack_start(self._overlay, expand=True, fill=True, padding=0)

        self.show_all()

    def set_filter_names(self, filter_names, default):
        map(self._add_filter_option, filter_names)
        self._filter_options[default].select()

    def _add_filter_option(self, filter_name):
        option = FilterOption(images_path=self._images_path, filter_name=filter_name,
            clicked_callback=lambda:self._presenter.on_filter_select(filter_name))
        self._filter_options[filter_name] = option
        align = Gtk.Alignment(xalign=0.5, yalign=0.0, xscale=0.0, yscale=0.0)
        align.add(option)
        self._scroll_contents.pack_start(align, expand=False, fill=False, padding=0)
        self.show_all()

    def select_filter(self, filter_name):
        for name, option in self._filter_options.items():
            if name == filter_name:
                option.select()
            else:
                option.deselect()

    def set_presenter(self, presenter):
        self._presenter = presenter

class FilterOption(Gtk.EventBox):
    """
    A selectable filter option with an image and caption.
    """
    def __init__(self, images_path="", filter_name="NORMAL", clicked_callback=None):
        super(FilterOption, self).__init__(name="filter-event-box")
        
        thumbnail_path = images_path + "/filter_thumbnails/filter_" + filter_name + ".jpg"
        
        self._filter_name = filter_name
        self._clicked_callback = clicked_callback
        self._filter_image = Gtk.Image(name="filter-image", file=thumbnail_path)
        self._filter_label = Gtk.Label(filter_name)

        self._vbox = Gtk.VBox(homogeneous=False, spacing=0)
        self._vbox.pack_start(self._filter_image, expand=False, fill=False, padding=0)
        self._vbox.pack_start(self._filter_label, expand=False, fill=False, padding=2)

        self.add(self._vbox)

        self.connect('leave-notify-event', self._on_mouse_leave)
        self.connect('enter-notify-event', self._on_mouse_enter)
        self.connect('button-release-event', self._on_button_release)

    def select(self):
        flags = self._filter_image.get_state_flags() | Gtk.StateFlags.SELECTED
        self._filter_image.set_state_flags(flags, True)

    def deselect(self):
        flags = Gtk.StateFlags(self._filter_image.get_state_flags() & ~Gtk.StateFlags.SELECTED)
        self._filter_image.set_state_flags(flags, True)

    def _on_mouse_enter(self, event, data=None):
        flags = self._filter_image.get_state_flags() | Gtk.StateFlags.PRELIGHT
        self._filter_image.set_state_flags(flags, True)

    def _on_mouse_leave(self, event, data=None):
        flags = Gtk.StateFlags(self._filter_image.get_state_flags() & ~Gtk.StateFlags.PRELIGHT)
        self._filter_image.set_state_flags(flags, True)

    def _on_button_release(self, event, data=None):
        #if mouse is no longer over eventbox, don't select the filter
        if self._filter_image.get_state_flags() & Gtk.StateFlags.PRELIGHT == 0: return
        if self._clicked_callback != None:
            self._clicked_callback()
