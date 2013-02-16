import dbus.service


class DBusSingleAppInstance(dbus.service.Object):


    APP_NAME = 'org.social_bar.single_instance'
    APP_PATH = '/org/social_bar/single_instance'

    def __init__(self):
        name = dbus.service.BusName(self.APP_NAME, bus = dbus.SessionBus())
        super(DBusService, self).__init__(name, self.APP_PATH)

    @dbus.service.method(dbus_interface=APP_NAME)
    def run(self):
        self.app.window.present()

    @classmethod
    def is_running(self):
        app_name = dbus.SessionBus().request_name(self.APP_NAME)
        return app_name != dbus.bus.REQUEST_NAME_REPLY_PRIMARY_OWNER

    @classmethod
    def get_app(self):
        proxy_object = dbus.SessionBus().get_object(self.APP_NAME, self.APP_PATH)
        player = dbus.Interface(proxy_object, self.APP_NAME)
        return player

