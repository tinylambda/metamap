from django.utils.deprecation import MiddlewareMixin


class DjangoDataMiddleware(MiddlewareMixin):
    """Middleware for collecting data from django stack"""

    def __init__(self, get_response):
        super(DjangoDataMiddleware, self).__init__(get_response)
