import asyncio
import logging

from django.utils.decorators import sync_and_async_middleware
from django.utils.deprecation import MiddlewareMixin


class CoreMiddleware:
    """old style middleware"""

    def __init__(self, get_response):
        self.get_response = get_response

    # It should return either None or an HttpResponse object.
    # If it returns None, Django will continue processing this request,
    # executing any other process_view() middleware and, then, the appropriate view.
    # If it returns an HttpResponse object, Django won’t bother calling the appropriate view;
    # it’ll apply response middleware to that HttpResponse and return the result.
    def process_view(self, request, view_func, view_args, view_kwargs):
        logging.info(
            "process_view in %s, %s", self, asyncio.iscoroutinefunction(view_func)
        )

    # Django calls process_exception() when a view raises an exception.
    # process_exception() should return either None or an HttpResponse object.
    # If it returns an HttpResponse object,
    # the template response and response middleware will be applied
    # and the resulting response returned to the browser. Otherwise, default exception handling kicks in.
    def process_exception(self, request, exception):
        logging.info("process_exception in %s", self)

    # process_template_response() is called just after the view has finished executing,
    # if the response instance has a render() method, indicating that it is a TemplateResponse or equivalent.
    #
    # It must return a response object that implements a render method.
    # It could alter the given response by changing response.template_name and response.context_data,
    # or it could create and return a brand-new TemplateResponse or equivalent.
    def process_template_response(self, request, response):
        logging.info("process_template_response in %s", self)
        return response

    def __call__(self, request):
        logging.info(
            "before view in %s, %s",
            self,
            asyncio.iscoroutinefunction(self.get_response),
        )
        response = self.get_response(request)
        logging.info("after view in %s", self)
        return response

    async def __acall__(self, request):
        pass


# @sync_and_async_middleware
# def simple_middleware(get_response):
#     # one-time configuration and initialization
#     def middleware(request):
#         logging.info("simple middleware")
#         response = get_response(request)
#         return response
#
#     return middleware
