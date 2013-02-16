import gtk
import webkit

class FBAuthView():
    
    def __init__(self, x=0, y=0, width=500, height=400, url=''):
        print 'Initializing fbauthview...'
        self.window = gtk.Window()
        self.window.set_decorated(False)
        self.window.set_resizable(False)
        self.window.set_size_request(width, height)
        self.window.move(x, y)
        self.scroller = gtk.ScrolledWindow()
        self.web_view = webkit.WebView()
        if url:
            self.web_view.show()
            self.web_view.open(url)
        self.scroller.add(self.web_view)
        self.window.add(self.scroller)
        print '-- done.'
    
    def destroy(self):
        self.window.destroy()
    
    def show(self):
        self.window.show()
    
    def show_all(self):
        print 'show_all of fbauthview called...'
        self.window.show_all()
        print '-- done.'
    def open(self, url):
        self.web_view.open(url)
        