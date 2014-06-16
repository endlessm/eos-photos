import urllib
import urllib2
import urlparse
from gi.repository import Gtk, WebKit2


class FacebookAuthDialog(Gtk.Dialog):
    __gtype_name__ = 'FacebookAuthDialog'
    # -- DEV --
    #FB_APP_ID = '393860344022808'
    #FB_APP_SECRET = 'eb0dcb05f7512be39f7a3826ce99dfcd'
    # -- PRODUCTION --
    FB_APP_ID = '407909575958642'
    FB_APP_SECRET = '496f85b88366ae40b42d16579719815c'

    def __init__(self, **kw):
        kw.setdefault('default_width', 600)
        kw.setdefault('default_height', 400)
        kw.setdefault('modal', True)
        kw.setdefault('destroy_with_parent', True)
        super(FacebookAuthDialog, self).__init__(**kw)
        self._access_token = None
        self._message = ""

        self.web_view = WebKit2.WebView(expand=True)
        self.web_view.load_uri('http://graph.facebook.com/oauth/authorize?scope=read_stream%2Cpublish_stream&redirect_uri=http%3A%2F%2Flocalhost%3A8080%2F&display=popup&client_id=' + self.FB_APP_ID)
        self.web_view.connect('close', self._on_close)
        self.web_view.connect('load-failed', self._on_load_failed)
        self.web_view.connect('load-changed', self._on_load_changed)
        self.web_view.show_all()
        self.get_content_area().add(self.web_view)

    def get_access_token(self):
        return self._access_token

    def get_message(self):
        return self._message

    def _end_dialog(self, reponse):
        self.web_view.destroy()
        self.response(reponse)

    def _on_close(self, web_view):
        # The facebook webview has requested the window be close, this
        # probably means the user clicked cancel.
        self._message = _("Login canceled.")
        self._end_dialog(0)

    def _on_load_failed(self, web_view, load_event, failing_uri, error):
        print "Load failed"
        self._message = _("Could not reach facebook.")
        self._end_dialog(0)

    def _on_load_changed(self, view, load_event):
        uri = view.get_uri()
        parsed = urlparse.urlparse(uri)

        # When the login flow eventually moves to a page other than the one specified in
        # the original webkit load_uri call, all calls to window.close() will fail
        # (https://developer.mozilla.org/en-US/docs/Web/API/Window.close)
        # So instead override the close function to reload the current URI with an error
        # parameter to abort the login flow
        script = """
            window.close = function(){
                loc = window.location.toString()
                if(loc.indexOf('?') === -1)
                    loc += '?';
                else
                    loc += '&';
                window.location = loc + 'error=WINDOW_CLOSED'
            }
            """
        view.run_javascript(script, None, None, None)

        parsed_query = urlparse.parse_qs(parsed.query)
        if parsed_query.has_key('code') and self._access_token is None:
            code = parsed_query['code'][0]
            self._query_access_token(code)
            return True
        elif parsed_query.has_key('error'):
            self._message = _("Login canceled.")
            self._end_dialog(0)
        return False
    
    def _query_access_token(self, code):
        url = 'https://graph.facebook.com/oauth/access_token'
        params = {'client_id': self.FB_APP_ID,
                  'redirect_uri':'http://localhost:8080/',
                  'client_secret': self.FB_APP_SECRET,
                  'code':code}
        url = url + '?' + urllib.urlencode(params)
        try:
            response = urllib2.urlopen(url).read()
            self._access_token = urlparse.parse_qs(response)['access_token'][0]
            self._end_dialog(1)
        except Exception as e:
            self._message = _("Could not reach facebook.")
            self._end_dialog(0)
