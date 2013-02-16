import os
import json

class SocialBarModel:
    def __init__(self):
        self.LOCAL_FACEBOOK_FILE = os.path.expanduser('~/.fb_access_token')
        self.USER_IMAGES_LOCATION = os.path.expanduser('~/.endlessm/social_bar/images/')
        self.LOCAL_IMAGES_LOCATION = os.path.expanduser('/usr/share/eos-social/images/')
        self.LOCAL_SETTINGS_FILE = os.path.expanduser('~/.social_bar_settings')
        
    def get_stored_fb_access_token(self):
        if os.path.exists(self.LOCAL_FACEBOOK_FILE):
            return open(self.LOCAL_FACEBOOK_FILE).read()
        else:
            return None
    
    def save_fb_access_token(self, token):
        if token:
            try:
                open(self.LOCAL_FACEBOOK_FILE,'w').write(token)
                return True
            except:
                return False
        else:
            return False

    def _load_setting(self):
        try:
            if not os.path.isfile(self.LOCAL_SETTINGS_FILE):
                return {}
            with open(self.LOCAL_SETTINGS_FILE,'r') as f:
                content = f.read()
                f.close()
                return json.loads(content)
        except:
            return {}

    def _store_setting(self, content):
        try:
            with open(self.LOCAL_SETTINGS_FILE,'w') as f:
                json_content = json.dumps(content)
                f.write(json_content)
                f.close()
        except:
            pass

    def get_stored_picture_file_path(self):
        return self.USER_IMAGES_LOCATION + 'avatar'

    def get_no_picture_file_path(self):
        return self.LOCAL_IMAGES_LOCATION + 'no_image.jpg'

    def get_logout_on_shutdown_active(self):
        content = self._load_setting()
        return content.get('logout_on_shutdown', False)

    def set_logout_on_shutdown_active(self, state):
        if state != True:
            state = False
        content = self._load_setting()
        content['logout_on_shutdown'] = state
        self._store_setting(content)

    def logout(self):
        try:
            os.remove(self.LOCAL_FACEBOOK_FILE)
        except:
            pass

