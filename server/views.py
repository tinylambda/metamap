from pprint import pprint

from django.http import HttpResponse
from django.shortcuts import render
from django.views import View


class ServerView(View):
    def get(self, request):
        pprint(self.request.META)
        return HttpResponse('Hello servers')