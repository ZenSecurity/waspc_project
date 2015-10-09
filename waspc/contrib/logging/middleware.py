from datetime import datetime
from logging import getLogger
# from time import time


class LoggingMiddleware(object):
    def __init__(self):
        self.logger = getLogger('waspc')

    # def process_request(self, request):
    #     request.timer = time()
    #     return None

    def process_response(self, request, response):
        print dir(request)
        self.logger.info('[{0:%d}/{0:%b}/{0:%Y} {0:%X}] "{method} {path} {protocol}" {status} {content_length}'.format(
            datetime.now(),
            method=request.method,
            path=request.get_full_path(),
            protocol=request.environ['SERVER_PROTOCOL'],
            status=response.status_code,
            content_length=len(response.content),
            # generation_time=time() - request.timer
        ))
        if request.body:
            self.logger.info(request.body)

        return response
