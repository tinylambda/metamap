from django.http import HttpResponse
from django.views import View


class ServerView(View):
    def get(self, request):
        return HttpResponse('Hello servers')
