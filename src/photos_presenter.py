class PhotosPresenter(object):
    def __init__(self, model=None, view=None):
        self._model = model
        self._view = view
        self._view.set_presenter(self)

    def close(self):
        # Prompt for save?
        self._view.close_window()

    def minimize(self):
        self._view.minimize_window()

    def open(self):
        print "Open called"

    def save(self):
        print "Save called"

    def share(self):
        print "Share called"

