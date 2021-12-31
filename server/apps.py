import importlib
import inspect
import logging
import os.path

from django.apps import AppConfig


class ServerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'server'

    def ready(self):
        from server import servers
        servers_module = inspect.getmodule(servers)

        logging.info('loading all server implementations from server.servers module')
        servers_module_file = inspect.getfile(servers)
        servers_path = os.path.dirname(servers_module_file)
        for item in os.listdir(servers_path):
            full_path = os.path.join(servers_path, item)
            if os.path.isdir(full_path) and not item.startswith('__'):
                importlib.import_module(f'.{item}', servers_module.__name__)
