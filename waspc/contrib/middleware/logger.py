from datetime import datetime
from logging import getLogger
from time import time


class RequestLoggerMiddleware(object):
    def __init__(self):
        self.logger = getLogger('waspc')
        self.request_body = None

    def process_request(self, request):
        request.timer = time()

        if request.body:
            self.request_body = request.body

        return None

    def process_response(self, request, response):
        try:
            self.logger.info(
                '[{0:%d}/{0:%b}/{0:%Y} {0:%X}] '
                '"{method} {path} {protocol}" '
                '{status} {content_length} {generation_time:.2f}s'.format(
                    datetime.now(),
                    method=request.method,
                    path=request.get_full_path(),
                    protocol=request.environ['SERVER_PROTOCOL'],
                    status=response.status_code,
                    content_length=len(response.content),
                    generation_time=time() - request.timer
                )
            )

            if self.request_body:
                self.logger.info(request.body)
                self.request_body = None

        except AttributeError as exception:
            self.logger.error('[{0:%d}/{0:%b}/{0:%Y} {0:%X}] {exception}'.format(datetime.now(), exception=exception))

        return response
