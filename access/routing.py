from django.urls import re_path

from access.consumers import AccessConsumer

websocket_urlpatterns = [
    re_path(r'ws/access/(?P<group_name>\w+)/$', AccessConsumer.as_asgi()),
]
