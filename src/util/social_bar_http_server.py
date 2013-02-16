from BaseHTTPServer import HTTPServer

class SocialBarHttpServer(HTTPServer):
    def serve_forever(self):
        self.should_run = True
        while self.should_run:
            self.handle_request()