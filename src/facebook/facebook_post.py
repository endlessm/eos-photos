import datetime
import calendar
from math import floor
import pprint

class FacebookPost:
    def __init__(self, data):
        self.id = data['post_id']
        self.poster = data['who']['name']
        self.poster_id = data['actor_id']
        self.poster_image = data['who']['pic_square']
        self.image = self.get_image(data)
        self.subject = ''
        self.actions = {}
        self.likes = {}
        self.comments = {}
        self.type = data['type']
        self.url = self.get_url(data)
        self.text = self.get_text(data)
        if data.has_key('description'):
            self.subject = data['description']
        
        if not self.text and not self.subject:
            self.text = '\n' + self.poster + _(' posted on Facebook.') + '\n'
        
        self.text = self.text.replace('\n','<br/>')
        
        self.date_created = data['created_time']
        self.date_updated = data['updated_time']
        now = calendar.timegm(datetime.datetime.utcnow().utctimetuple())
        self.time_elapsed = now - self.date_created
        self.time_elapsed_string = self.get_elapsed_string(self.time_elapsed)
        
        if data.has_key('likes'):
            self.likes = data['likes']
        
        if data.has_key('comments'):
            self.comments = data['comments']
    
    def __str__(self):
        rv =  'id      : ' + self.id + '\n'
        rv += 'from    : ' + self.poster + '\n'
        rv += 'avatar  : ' + self.poster_image + '\n'
        rv += 'subject : ' + self.subject + '\n'
        rv += 'text    : ' + self.text + '\n'
        rv += 'image   : ' + self.image + '\n'
        rv += 'created : ' + self.date_created + '\n'
        rv += 'updated : ' + self.date_updated + '\n'
        rv += 'likes   : ' + unicode(self.likes) + '\n'
        rv += 'comments: ' + unicode(self.comments) + '\n'
        rv += 'actions : ' + unicode(self.actions) + '\n'
        rv += '-'*80
        return rv
    
    def get_elapsed_string(self, delta):
        if delta < 0:
            return _('less than a minute ago')
        days = int(floor(delta/(60*60*24)))
        hours = int(floor(delta/(60*60)))
        minutes = int(floor(delta/60))
        if days > 0:
            return self.pluralize(days, 'DAY')
        
        if hours > 0:
            return self.pluralize(hours, 'HOUR')
        
        if minutes > 0:
            return self.pluralize(minutes, 'MINUTE')
    
    def pluralize(self, num, period_name):
        if num == 1:
            return self.singular(num, period_name)
        else:
            return self.plural(num, period_name)
    
    def singular(self, num, period_name):
        if period_name == 'DAY':
            return str(num) + ' ' + _('day ago')
        if period_name == 'HOUR':
            return str(num) + ' ' + _('hour ago')
        if period_name == 'MINUTE':
            return str(num) + ' ' + _('minute ago')
        if period_name == 'SECOND':
            return _('less than a minute ago')
    
    def plural(self, num, period_name):
        if period_name == 'DAY':
            return str(num) + ' ' + _('days ago')
        if period_name == 'HOUR':
            return str(num) + ' ' + _('hours ago')
        if period_name == 'MINUTE':
            return str(num) + ' ' + _('minutes ago')
        if period_name == 'SECOND':
            return _('less than a minute ago')
    
    def get_url(self, data):
        if data['permalink']:
            return data['permalink']
        else:
            if self.type == 361:
                parts = self.id.split('_')
                return 'http://www.facebook.com/' + parts[0] + '/posts/' + parts[1]
            else:
                return 'http://www.facebook.com/' + str(self.poster_id)
    
    def get_text(self, data):
        text = ''
        if data['message']:
            text = data['message']
        else:
            if data['attachment'].has_key('caption') and data['attachment']['caption']:
                text = data['attachment']['caption']
            elif data['attachment'].has_key('description') and data['attachment']['description']:
                text = data['attachment']['description']
            elif data['attachment'].has_key('name'):
                text = data['attachment']['name']
        return text
    
    def get_image(self, data):
        image = ''
        if data['attachment']:
            if data['attachment'].has_key('media'):
                if data['attachment']['media']:
                    image = data['attachment']['media'][0]['src']
        return image
        
