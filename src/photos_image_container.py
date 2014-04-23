from gi.repository import GtkClutter, Clutter


class ImageContainer(GtkClutter.Embed):
    """
    Embeds the clutter image and sizes the image to fit centered in the space allotted.
    """
    def __init__(self, **kw):
        kw.setdefault("use-layout-size", True)
        super(ImageContainer, self).__init__(**kw)
        self._stage = self.get_stage()
        self._stage.set_layout_manager(Clutter.BinLayout())
        self._image_widget = None

    # We need to make sure this allocation is the right aspect ratio for our
    # image, or there will be an obnoxiously oversized stage with a shadow
    # even if our image is sized correctly within the stage. There's no way to
    # quite do this properly with a size request as we don't know whether we
    # need width for height or height for width till we get the allocation. So
    # we do this directly in the size_allocate method
    def do_size_allocate(self, alloc):
        im_ratio = self._image_widget.get_ratio()
        if self._image_widget != None:
            alloc_ratio = float(alloc.width) / alloc.height
            if im_ratio < alloc_ratio:
                old_width = alloc.width
                alloc.width = alloc.height * im_ratio
                alloc.x += (old_width - alloc.width) / 2
            else:
                old_height = alloc.height
                alloc.height = alloc.width / im_ratio
                alloc.y += (old_height - alloc.height) / 2
        GtkClutter.Embed.do_size_allocate(self, alloc)

    def set_image_widget(self, image_widget):
        self._stage.add_child(image_widget)
        self._image_widget = image_widget

    def set_fullscreen_mode(self, fullscreen):
        self._fullscreen_mode = fullscreen
        # if fullscreen:
        #     self._stage.add_child(self._unfullscreen_button)
        #     if self._fullscreen_button.get_parent() == self._stage:
        #         self._stage.remove_child(self._fullscreen_button)
        # else:
        #     self._stage.add_child(self._fullscreen_button)
        #     if self._unfullscreen_button.get_parent() == self._stage:
        #         self._stage.remove_child(self._unfullscreen_button)

    def set_presenter(self, presenter):
        self._presenter = presenter
