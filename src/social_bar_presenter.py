from util.util import CSS, SLICKSCROLL_CSS, SLICKSCROLL_JS, MOUSE_WHEEL_JS, posts_query, users_query, older_posts_query
from facebook.facebook import GraphAPIError, GraphAPI
from facebook.facebook_posts import FacebookPosts
import subprocess
from urllib2 import URLError
from Cheetah.Template import Template
import urlparse
import json
import pprint
import webbrowser
import simplejson
import urllib2
import gettext

gettext.install('eos-social', '/usr/share/locale', unicode=True, names=['ngettext'])

class SocialBarPresenter:


    # -- DEV --
    #FB_APP_ID = '393860344022808'
    #FB_APP_SECRET = 'eb0dcb05f7512be39f7a3826ce99dfcd'
    # -- PRODUCTION --
    FB_APP_ID = '407909575958642'
    FB_APP_SECRET = '496f85b88366ae40b42d16579719815c'

    def __init__(self, view=None, model=None):
        self._view = view
        self._model = model
        self._app_id = self.FB_APP_ID
        self._app_secret = self.FB_APP_SECRET
        self._fb_graph_url = 'graph.facebook.com'
        self._webserver_url = 'http://localhost:8080/'
        self._fb_access_token = None #self._model.get_stored_fb_access_token()
        print self._fb_access_token
        if self._fb_access_token:
            self._graph_api = GraphAPI(access_token=self._fb_access_token)
        else:
            self._graph_api = None

    def get_view(self):
        return self._view

    def get_model(self):
        return self._model
        
    def get_fb_news_feed(self, callback=None):
        query = {'posts':posts_query,'users':users_query}
        try:
            result = self._graph_api.fql(query)
        except GraphAPIError as error:
            self.oauth_exception_handler(error.result)
            return None
        except URLError as e:
            self.url_exception_handler()
            return None
        except:
            return None        
        
        if result:
            result =  self.parse_posts(result)
            html = str(self.render_posts_to_html(result.posts, result.previous_url, result.next_url))
            self._view.load_html(html)
        
        if callback:
            callback(result)
        else:
            return result
    
    def fb_login(self, callback=None):
        proc = subprocess.Popen(['python', '/usr/share/eos-social/facebook/fb_auth_window.pyc'], stdout=subprocess.PIPE)
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
            return True
        except GraphAPIError as error:
            self.oauth_exception_handler(error.result)
            return False
        except URLError as e:
            self.url_exception_handler()
            return False
        except:
            return False

    
    def post_to_fb(self, text):
        try:
            self._graph_api.put_wall_post(text)
            #self.get_fb_news_feed()
            return True
        except GraphAPIError as error:
            self.oauth_exception_handler(error.result)
            return False
        except URLError as e:
            self.url_exception_handler()
            return False
        except:
            return False
    
    def post_fb_like(self, id):
        try:
            self._graph_api.put_like(id)
            return True
        except GraphAPIError as error:
            self.oauth_exception_handler(error.result)
            return False
        except URLError as e:
            self.url_exception_handler()
            return False
        except:
            return False
    
    def post_fb_comment(self, id, comment):
        try:
            self._graph_api.put_comment(id, comment)
            return True
        except GraphAPIError as error:
            self.oauth_exception_handler(error.result)
            return False
        except URLError as e:
            self.url_exception_handler()
            return False
        except:
            return False
        
    def get_new_fb_posts(self, callback, stamp):
        query = {'posts':older_posts_query % str(stamp),'users':users_query}
        try:
            result = self._graph_api.fql(query)
            return result
        except GraphAPIError as error:
            self.oauth_exception_handler(error.result)
            return None
        except URLError as e:
            self.url_exception_handler()
            return None
        except:
            return None
    
#    def show_fb_login(self):
#        self._view.show_fb_auth_popup()
    
    def set_fb_access_token(self, token):
        self._fb_access_token = token
        self._model.save_fb_access_token(token)
    
    def oauth_exception_handler(self, result):
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
            self._view.show_popup_notification(message)
        if code in oauth_error_codes or code in permissions_error_codes or code == 606:
            self.fb_login()
    
    def url_exception_handler(self):
        message = _('Network problem detected. Please check your internet connection and try again.')
        self._view.show_popup_notification(message)
        
    def render_posts_to_html(self, posts, newer_url='', older_url=''):
        params = [{'posts':posts},
                  {'css':CSS},
                  {'mousewheel_js':MOUSE_WHEEL_JS},
                  {'slickscroll_js':SLICKSCROLL_JS},
                  {'slickscroll_css':SLICKSCROLL_CSS},
                  {'newer':newer_url}, {'older':older_url},
                  {'like_string':_('like')},
                  {'comment_string':_('comment')}]
        #@TODO: fix path and file name
        page = Template(file = '/usr/share/eos-social/templates/news-feed.html', searchList = params)
        return page
    
    def navigator(self, uri):

        def register_scheme(scheme):
            for method in filter(lambda s: s.startswith('uses_'), dir(urlparse)):
                getattr(urlparse, method).append(scheme)

        register_scheme('eossocialbar')
        parsed = urlparse.urlparse(uri)
        parsed_query = urlparse.parse_qs(parsed.query)

        if parsed.path == 'LIKE':
            result = self.post_fb_like(parsed_query['id'][0])
            if result:
                script = 'like_success(%s, %s);' % (json.dumps(parsed_query['id'][0]), json.dumps(_('liked')))
                self._view._browser.execute_script(script)
        elif parsed.path == 'UNLIKE':
            pass
            #unliking as described in FB documentation does not work
        elif parsed.path == 'VIEWPOST':
            webbrowser.open(parsed.query[4:], new=1, autoraise=True)
        elif parsed.path == 'COMMENT':
            self.display_comments(parsed_query)
        elif parsed.path == 'POST_COMMENT':
            result = self.post_fb_comment(parsed_query['id'][0], parsed_query['comment_text'][0])
            self.get_fb_news_feed()
        elif parsed.path == 'VIEW_POSTER':
            webbrowser.open('http://www.facebook.com/'+parsed_query['poster_id'][0], new=1, autoraise=True)
        elif parsed.path.startswith('GET_OLDER_POSTS'):
            self.get_older_posts(parsed)
        elif parsed.path.startswith('GET_NEWER_POSTS'):
            self.get_fb_news_feed()
        return 1
        
    def get_commments(self, post_id):
        raw_comments = self._graph_api.request(post_id+'/comments')
        return raw_comments
    
    def generate_posts_elements(self, posts):
        params = [{'posts':posts},
                  {'like_string':_('like')},
                  {'comment_string':_('comment')}]
        #@TODO: fix path and file name
        page = Template(file = '/usr/share/eos-social/templates/posts-array.html', searchList = params)
        return page

#    def get_fb_user(self, fb_user_id='me'):
#        return

    def show_profil_page(self):
        if self._graph_api is None:
            self.show_fb_login()
            return
        profile = self._graph_api.get_object("me")
        webbrowser.open('http://www.facebook.com/' + profile['id'])

    def get_profil_picture(self):
        if self._graph_api is None:
            return None
        profile = self._graph_api.get_object("me")
        image_url = 'https://graph.facebook.com/' + profile['id'] + '/picture'
        self.get_image_dwn(image_url)
        return

    def get_profil_display_name(self):
        if self._graph_api is None:
            return ''
        
        try:
            profile = self._graph_api.get_object("me")
            if profile:
                return profile['name']
        except:
            return ''

    def get_stored_picture_file_path(self):
        return self._model.get_stored_picture_file_path()

    def get_no_picture_file_path(self):
        return self._model.get_no_picture_file_path()

    def get_image_dwn(self, image_url):
        try:
            url_response = urllib2.urlopen(image_url)
            image_final_url = url_response.geturl()
            if image_final_url[-3:] in ('jpg', 'png', 'gif'):
                image_data = url_response.read()
                with open(self.get_stored_picture_file_path(), 'w') as f:
                    f.write(image_data)
                    f.close()
                return
        except:
            pass
        print 'error:', 'no image', image_final_url
        return

    def is_user_loged_in(self):
        if self._fb_access_token is None or not self.is_token_valid():
            return False
        else:
            return True
    
#    def get_html(self):
#        #@TODO: FOR DEBUGGING, NOT NEEDED IN PRODUCTION
#        self._view._browser.execute_script('oldtitle=document.title;document.title=document.documentElement.innerHTML;')
#        html = self._view._browser.get_main_frame().get_title()
#        return html

    def get_logout_on_shutdown_active(self):
        return self._model.get_logout_on_shutdown_active()

    def set_logout_on_shutdown_active(self, state):
        self._model.set_logout_on_shutdown_active(state)

    def logout(self):
        self._fb_access_token = None
        self._model.logout()
    
    def parse_posts(self, result):
        posts = []
        users = []
        for res_set in result:
            if res_set['name'] == 'posts':
                posts = res_set['fql_result_set']
            else:
                users = res_set['fql_result_set']
        
        for post in posts:
            for user in users:
                if post['actor_id'] == user['id']:
                    post['who'] = user
                    break
        
        return FacebookPosts(posts)
    
    def display_comments(self, parsed_query):
        comments = self.get_commments(parsed_query['id'][0])
        comments['data'].reverse()
        if len(comments['data']) > 4:
            to_show = comments['data'][:4]
        else:
            to_show = comments['data'][:len(comments['data'])]
        to_show.reverse()
        script = 'show_comments(%s, %s);' % (json.dumps(parsed_query['id'][0]), json.dumps(to_show))
        self._view._browser.execute_script(script)
    
    def get_older_posts(self, parsed):
        url = parsed.path.split('?url=')[1]
        result = self.get_new_fb_posts(None, url)
        result = self.parse_posts(result)
        if not result:
            return
        
        if not hasattr(result, 'posts'):
            return
        
        html = self.generate_posts_elements(result.posts)
        script = 'show_older_posts(%s, %s);' % (simplejson.dumps(str(html)), simplejson.dumps(result.next_url))
        self._view._browser.execute_script(script)
    
    def is_token_valid(self, token=''):
        if not token:
            token = self._fb_access_token
        try:
            temp_api = GraphAPI(access_token=token)
            resp = temp_api.request('me/home')
            return True
        except:
            return False

