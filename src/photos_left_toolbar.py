from gi.repository import Gtk
from widgets.list_button import ListButton

class PhotosLeftToolbar(Gtk.VBox):
    """
    The left filter selection toolbar for the photo app.
    """
    def __init__(self, images_path="", **kw):
        super(PhotosLeftToolbar, self).__init__(homogeneous=False, spacing=0, **kw)
        self._images_path = images_path

        self._categories = {}

        self._borders_image = Gtk.Image.new_from_file(images_path + "Filter-icon.png")
        self._borders_label = Gtk.Label(label="BORDERS", name="borders-title")
        self._borders_title_box = Gtk.HBox(homogeneous=False, spacing=0)
        self._borders_title_box.pack_start(self._borders_image, expand=False, fill=False, padding=0)
        self._borders_title_box.pack_start(self._borders_label, expand=False, fill=False, padding=2)
        self._borders_title_allign = Gtk.HBox(homogeneous=False, spacing=0)
        self._borders_title_allign.pack_start(self._borders_title_box, expand=False, fill=False, padding=10)


        borders_category = Category(images_path=self._images_path,label_name="BORDERS", category_name="borders",
            clicked_callback=lambda: self.change_category("borders"))

        filters_category = Category(images_path=self._images_path,label_name="FILTROS", category_name="filters",
            clicked_callback=lambda: self.change_category("filters"))

        self._categories["filters"] = filters_category
        self._categories["borders"] = borders_category


        #self._scroll_contents = Gtk.VBox(homogeneous=False, spacing=8)
        self._filter_options = {}

        # self._scroll_area = Gtk.ScrolledWindow(name="filters-scroll-area")
        # self._scroll_area.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        # self._scroll_area.add_with_viewport(self._scroll_contents)

        # self._drop_shadow = Gtk.Image.new_from_file(images_path + "Filter-mask-shadow.png")
        # self._drop_shadow.set_halign(Gtk.Align.CENTER)
        # self._drop_shadow.set_valign(Gtk.Align.START)
        # self._overlay = Gtk.Overlay()
        # self._overlay.add(self._scroll_area)
        # self._overlay.add_overlay(self._drop_shadow)

        #self.pack_start(self._borders_title_allign, expand=False, fill=False, padding=20)
        self.pack_start(filters_category, expand=True, fill=True, padding=20)
        self.pack_start(borders_category, expand=True, fill=True, padding=20)

        #self.pack_start(self._overlay, expand=True, fill=True, padding=0)

        self.show_all()

    def set_filter_names(self, filter_names, default):
        map(self._add_filter_option, filter_names)
        self._filter_options[default].select()

    def _add_filter_option(self, filter_name):
        category = self._categories["filters"]
        
        path = "filter_thumbnails/filter_" + filter_name + ".jpg"
        option = ListButton(images_path = self._images_path, path=path, name="filter", label_name=filter_name,
            clicked_callback=lambda: self._presenter.on_filter_select(filter_name), vertical=True)
        self._filter_options[filter_name] = option

        category.add_to_scroll(option)

    def select_filter(self, filter_name):
        for name, option in self._filter_options.items():
            if name == filter_name:
                option.select()
            else:
                option.deselect()

    def set_presenter(self, presenter):
        self._presenter = presenter

    def change_category(self, category_name):
        for name, category in self._categories.items():
            if name == category_name:
                category.select()
                category.expander.set_expanded(True)
                #category.expanded_cb(category.expander, None)
            else:
                category.deselect()
                category.expander.set_expanded(False)


class Category(Gtk.VBox):
    def __init__(self, images_path="", label_name="", category_name="", clicked_callback=None, **kw):
        super(Category, self).__init__(homogeneous=False, spacing=0, **kw)
        
        self._images_path = images_path
        self.title_box = ListButton(images_path=self._images_path, path="Filter-icon.png", name="filter",
        label_name=label_name, clicked_callback=clicked_callback, vertical=False)
        #self._title_allign = Gtk.HBox(homogeneous=False, spacing=0)
        #self._title_allign.pack_start(borders_title_box, expand=False, fill=False, padding=10)

        self.expander = Gtk.Expander()

        self.expander.connect('notify::expanded', self.expanded_cb)

        self._scroll_contents = Gtk.VBox(homogeneous=False, spacing=8)

        self._scroll_area = Gtk.ScrolledWindow(name="filters-scroll-area")
        self._scroll_area.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self._scroll_area.add_with_viewport(self._scroll_contents)

        # self._drop_shadow = Gtk.Image.new_from_file(images_path + "Filter-mask-shadow.png")
        # self._drop_shadow.set_halign(Gtk.Align.CENTER)
        # self._drop_shadow.set_valign(Gtk.Align.START)
        # self._overlay = Gtk.Overlay()
        # self._overlay.add(self._scroll_area)
        # self._overlay.add_overlay(self._drop_shadow)

        self.pack_start(self.title_box, expand=False, fill=False, padding=20)
        self.pack_start(self.expander, expand=True, fill=True, padding=20)
        #self.pack_start(self._scroll_area, expand=True, fill=True, padding=20)

        self.show_all()

    def expanded_cb(self, expander, params):
        if expander.get_expanded():
            expander.add(self._scroll_area)
            self._scroll_area.show()
        else:
            expander.remove(self._scroll_area)
        self.show_all()

    def select(self):
        self.title_box.select()
        self._scroll_area.show()

    def deselect(self):
        self.title_box.deselect()
        self._scroll_area.hide()


    def add_to_scroll(self, object_):
        align = Gtk.HBox(homogeneous=False, spacing=0)
        align.pack_start(object_, expand=False, fill=False, padding=30)
        self._scroll_contents.pack_start(align, expand=False, fill=False, padding=0)
        self.show_all()