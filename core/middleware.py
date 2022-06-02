import asyncio
import json
import logging
import threading

from channels.http import AsgiRequest
from django.utils.decorators import sync_and_async_middleware
from django.utils.deprecation import MiddlewareMixin


class CoreMiddleware(MiddlewareMixin):
    """old style middleware"""

    # It should return either None or an HttpResponse object.
    # If it returns None, Django will continue processing this request,
    # executing any other process_view() middleware and, then, the appropriate view.
    # If it returns an HttpResponse object, Django won’t bother calling the appropriate view;
    # it’ll apply response middleware to that HttpResponse and return the result.
    async def process_view(self, request, view_func, view_args, view_kwargs):
        logging.info(
            "process_view in %s, %s", self, asyncio.iscoroutinefunction(view_func)
        )

    # Django calls process_exception() when a view raises an exception.
    # process_exception() should return either None or an HttpResponse object.
    # If it returns an HttpResponse object,
    # the template response and response middleware will be applied
    # and the resulting response returned to the browser. Otherwise, default exception handling kicks in.
    async def process_exception(self, request, exception):
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

    def __call__(self, request: AsgiRequest):
        logging.info("dir(request): %s", dir(request))
        logging.info("META %s", json.dumps(request.META))
        logging.info("scope %s", dict(request.scope))
        logging.info("COOKIES %s", json.dumps(request.COOKIES))
        logging.info("FILES %s", json.dumps(request.FILES))
        logging.info("GET %s", json.dumps(request.GET))
        logging.info("POST %s", json.dumps(request.POST))
        logging.info("accepted_types: %s", request.accepted_types)
        logging.info("accepts: %s", request.accepts)
        logging.info("body: %s", request.body)
        logging.info("body_receive_timeout: %s", request.body_receive_timeout)
        logging.info("build_absolute_uri: %s", request.build_absolute_uri)
        logging.info("content_params: %s", request.content_params)
        logging.info("content_type: %s", request.content_type)
        logging.info("encoding: %s", request.encoding)
        logging.info("headers: %s", request.headers)
        logging.info("is_secure: %s", request.is_secure)
        logging.info("method: %s", request.method)
        logging.info("path: %s", request.path)
        logging.info("path_info: %s", request.path_info)
        logging.info("scheme: %s", request.scheme)
        logging.info("script_name: %s", request.script_name)
        logging.info("user: %s", request.user)
        logging.info("sync?: %s", self.sync_capable)
        logging.info("async?: %s", self.async_capable)

        if asyncio.iscoroutinefunction(self.get_response):
            return self.__acall__(request)

        logging.info("before get_response, %s", threading.current_thread().name)
        response = self.get_response(request)
        logging.info("after get_response, %s", threading.current_thread().name)
        return response

    async def __acall__(self, request):
        logging.info("async before get_response")
        response = await self.get_response(request)
        logging.info("async after get_response")
        return response


@sync_and_async_middleware
def simple_middleware(get_response):
    # one-time configuration and initialization
    if asyncio.iscoroutinefunction(get_response):

        async def middleware(request):
            logging.info("async simple middleware")
            response = await get_response(request)
            return response

    else:

        def middleware(request):
            logging.info("simple middleware")
            response = get_response(request)
            return response

    return middleware
