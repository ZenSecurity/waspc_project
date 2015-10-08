from logging import getLogger
from time import time


class LoggingMiddleware(object):
    def __init__(self):
        self.logger = getLogger('waspc')

    def process_request(self, request):
        request.timer = time()
        return None

    def process_response(self, request, response):
        print dir(request)
        print
        print dir(response)
        self.logger.info(
            '[%s] "%s %s" %s (%.1fs)',

            request.method,
            request.get_full_path(),
            response.status_code,
            time() - request.timer
        )
        return response
