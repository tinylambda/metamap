from django.utils.deprecation import MiddlewareMixin


class CoreMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        super(CoreMiddleware, self).__init__(get_response)
