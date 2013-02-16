import gtk
import gobject
import webkit
import urllib
import urllib2
import urlparse

class FBAuthWindow(gtk.Window):


    # -- DEV --
    #FB_APP_ID = '393860344022808'
    #FB_APP_SECRET = 'eb0dcb05f7512be39f7a3826ce99dfcd'
    # -- PRODUCTION --
    FB_APP_ID = '407909575958642'
    FB_APP_SECRET = '496f85b88366ae40b42d16579719815c'

    def __init__(self, presenter=None, url='', width=800, height=600):
        super(FBAuthWindow, self).__init__()
        self.set_title('Login')
        self._presenter = presenter
        self._authorized = False
        self.scroller = gtk.ScrolledWindow()
        self.web_view = webkit.WebView()
        self.web_view.connect("navigation-requested", self.on_navigation_requested)
        self.web_view.open('http://graph.facebook.com/oauth/authorize?scope=read_stream%2Cpublish_stream&redirect_uri=http%3A%2F%2Flocalhost%3A8080%2F&client_id=' + self.FB_APP_ID)
        self.web_view.show()
        self.scroller.add(self.web_view)
        self.scroller.show()
        self.add(self.scroller)
        self.set_size_request(width, height)
        self.set_position(gtk.WIN_POS_CENTER)
        self.show()
        self.connect("delete-event", self.on_destroy)
    
    def on_navigation_requested(self, view, frame, request, data=None):
        uri = request.get_uri()
        parsed = urlparse.urlparse(uri)
        parsed_query = urlparse.parse_qs(parsed.query)
        if parsed_query.has_key('code'):
            code = parsed_query['code'][0]
            token = self.get_access_token(code)
            if token:
                print 'ACCESS_TOKEN:' + token
                self._authorized = True
            self.emit("delete-event", gtk.gdk.Event(gtk.gdk.DELETE))
        elif parsed_query.has_key('error'):
            print 'ERROR occured.'
            self.emit("delete-event", gtk.gdk.Event(gtk.gdk.DELETE))
        return False
    
    def get_access_token(self, code):
        url = 'https://graph.facebook.com/oauth/access_token'
        params = {'client_id': self.FB_APP_ID,
                  'redirect_uri':'http://localhost:8080/',
                  'client_secret': self.FB_APP_SECRET,
                  'code':code}
        url = url + '?' + urllib.urlencode(params)
        try:
            response = urllib2.urlopen(url).read()
            token = urlparse.parse_qs(response)['access_token'][0]
            return token
        except:
            print 'EXCEPTION CAUGHT!!!'
            return None

        
    
    def on_destroy(self, *args, **kwargs):
        print 'Destroy signal caught.'
        if self._authorized:
            print 'SUCCESS'
        else:
            print 'FAILURE'
        self.window.destroy()
        gtk.main_quit()

    def main(self):
        gobject.threads_init()
        gtk.threads_init()
        gtk.main()


if __name__ == "__main__":
    t = FBAuthWindow()
    t.main()
