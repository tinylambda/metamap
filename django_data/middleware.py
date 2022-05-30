from django.utils.deprecation import MiddlewareMixin


class DjangoDataMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        super(DjangoDataMiddleware, self).__init__(get_response)
