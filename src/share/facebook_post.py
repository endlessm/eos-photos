from facebook import GraphAPIError, GraphAPI
from urllib2 import URLError
import subprocess
import pprint
import webbrowser

class FacebookPost:

    # -- DEV --
    #FB_APP_ID = '393860344022808'
    #FB_APP_SECRET = 'eb0dcb05f7512be39f7a3826ce99dfcd'
    # -- PRODUCTION --
    FB_APP_ID = '407909575958642'
    FB_APP_SECRET = '496f85b88366ae40b42d16579719815c'

    def __init__(self):
        self._app_id = self.FB_APP_ID
        self._app_secret = self.FB_APP_SECRET
        self._fb_access_token = None
        self._graph_api = None

    def fb_login(self, callback=None):
        # keep as dependency on social bar??
        # proc = subprocess.Popen(['python', '/usr/share/eos-social/facebook/fb_auth_window.pyc'], stdout=subprocess.PIPE)
        proc = subprocess.Popen(['python', '/usr/share/endless-os-photos/src/share/fb_auth_window.pyc'], stdout=subprocess.PIPE)
        for line in proc.stdout:
            print line
            if line.startswith('ACCESS_TOKEN:'):
                token = line.split(':')[1]
                if self.is_token_valid(token):
                    self.set_fb_access_token(token)
                    self._graph_api = GraphAPI(access_token=self._fb_access_token)
                else:
                    return
            elif line.startswith('FAILURE'):
                return

        if callback:
            callback()

    def post_image(self, file_name, message=""):
        try:
            self._graph_api.put_photo(open(file_name), message=message)
            return True, ""
        except GraphAPIError as error:
            return False, self.oauth_exception_message(error.result)
        except URLError as e:
            return False, self.url_exception_handler()
        except:
            print e
            return False, _("Post failed. We're not really sure what happened sorry!")
    
    def set_fb_access_token(self, token):
        self._fb_access_token = token

    def oauth_exception_message(self, result):
        server_error_codes = [1,2,4,17]
        oauth_error_codes = [102, 190]
        permissions_error_codes = range(200, 300)
        if 'error' in result:
            if 'code' in result['error']:
                code = result['error']['code']
        elif 'error_code' in result:
            code = result['error_code']
        if code in server_error_codes:
            message = _('Requested action is not possible at the moment. Please try again later.')
            return message
        if code in oauth_error_codes or code in permissions_error_codes or code == 606:
            message = _('Login failed.')
            return message
        return 
    
    def url_exception_message(self):
        message = _('Network problem detected. Please check your internet connection and try again.')
        return "Post failed. We're not really sure what happened sorry!"

    def is_user_loged_in(self):
        if self._fb_access_token is None or not self.is_token_valid():
            return False
        else:
            return True

    def logout(self):
        self._fb_access_token = None
        self._graph_api = None

    def is_token_valid(self, token=''):
        if not token:
            token = self._fb_access_token
        try:
            temp_api = GraphAPI(access_token=token)
            resp = temp_api.request('me/home')
            return True
        except:
            return False
