import logging
import time

logger = logging.getLogger('request_logger')


class RequestLoggingMiddleware:
    """
    Har bir so'rovni logga yozadi va javobga X-Response-Time headerini qo'shadi.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        response = self.get_response(request)

        duration = time.time() - start_time
        duration_ms = round(duration * 1000, 2)

        response['X-Response-Time'] = f'{duration_ms}ms'

        user = request.user if request.user.is_authenticated else 'Anonim'
        logger.info(
            '%s %s -> %s | %sms | user=%s',
            request.method,
            request.get_full_path(),
            response.status_code,
            duration_ms,
            user,
        )

        return response