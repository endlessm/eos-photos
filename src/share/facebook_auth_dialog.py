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
    FB_LOGIN_URL = 'https://www.facebook.com/dialog/oauth'
    # According to the developer docs, this redirect url should be used for all
    # desktop apps with an embedded login page.
    FB_REDIRCT_URL = 'https://www.facebook.com/connect/login_success.html'

    def __init__(self, **kw):
        kw.setdefault('default_width', 600)
        kw.setdefault('default_height', 400)
        kw.setdefault('modal', True)
        kw.setdefault('destroy_with_parent', True)
        super(FacebookAuthDialog, self).__init__(**kw)
        self._access_token = None
        self._message = ""

        self.web_view = WebKit2.WebView(expand=True)
        url = self.FB_LOGIN_URL
        params = {
            'client_id': self.FB_APP_ID,
            'redirect_uri': self.FB_REDIRCT_URL,
            'display': 'popup',
            'scope': 'publish_actions',
            'response_type': 'token',
        }
        url = url + '?' + urllib.urlencode(params)
        self.web_view.load_uri(url)
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
        if not uri.startswith(self.FB_REDIRCT_URL):
            return

        parsed = urlparse.urlparse(uri)
        parsed_fragment = urlparse.parse_qs(parsed.fragment)
        if parsed_fragment.has_key('access_token'):
            self._access_token = parsed_fragment['access_token'][0]
            self._end_dialog(1)
            return
        parsed_query = urlparse.parse_qs(parsed.query)
        if parsed_query.has_key('error'):
            self._message = _("Login canceled.")
        else:
            self._message = _('Login failed.')
        self._end_dialog(0)
        return
