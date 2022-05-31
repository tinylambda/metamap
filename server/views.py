from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt


@method_decorator(csrf_exempt, name="dispatch")
class ServerView(View):
    def __init__(self, **kwargs):
        super(ServerView, self).__init__(**kwargs)
        self.response_dict = {}

    def get(self, request):
        return JsonResponse(self.response_dict)


async def async_func(request):
    return JsonResponse(
        {
            "func": "async_func",
            "mode": "async",
        }
    )
