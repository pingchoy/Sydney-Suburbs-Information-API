class StatsCapture:

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        x = 1
        with open('request_log.txt', 'a') as f:
            path = environ['PATH_INFO']
            f.write(path)
            return self.app(environ, start_response)

