import os

from django.conf import settings
from django.core.management.base import CommandError
from django.template.loader import render_to_string

from core.management.commands._base import MetaCommand


class Command(MetaCommand):
    help = 'Create basic nginx configuration file for this project, ' \
           'you can change the generated conf file and deploy it to your nginx conf.d directory'

    def add_arguments(self, parser):
        parser.add_argument("action", nargs="?", help="specify the action you want to run", type=str)

    def prepare_configuration_files(self):
        http_conf_filename = getattr(settings, 'NGINX_HTTP_CONF_FILENAME', None)
        if http_conf_filename is None:
            raise CommandError('settings.NGINX_HTTP_CONF_FILENAME not specified')

        websocket_conf_filename = getattr(settings, 'NGINX_WEBSOCKET_CONF_FILENAME', None)
        if websocket_conf_filename is None:
            raise CommandError('settings.NGINX_WEBSOCKET_CONF_FILENAME not specified')

        http_conf_dirname = os.path.dirname(http_conf_filename)
        if not os.path.exists(http_conf_dirname):
            os.makedirs(http_conf_dirname)

        websocket_conf_dirname = os.path.dirname(websocket_conf_filename)
        if not os.path.exists(websocket_conf_dirname):
            os.makedirs(websocket_conf_dirname)

        settings_useful_for_nginx = [
            'STATIC_ROOT',
            'NGINX_HTTP_SERVER_NAME',
            'NGINX_WEBSOCKET_SERVER_NAME',
        ]

        nginx_context = {
            key: getattr(settings, key, None)
            for key in dir(settings)
            if key in settings_useful_for_nginx
        }

        if nginx_context['NGINX_HTTP_SERVER_NAME']:
            with open(http_conf_filename, 'w') as f:
                f.write(render_to_string('conf/nginx/default-http.conf', context=nginx_context))
                self.stdout.write(self.style.SUCCESS(f'written Nginx http conf to {http_conf_filename}'))
        else:
            self.stderr.write(self.style.WARNING(
                'NGINX_HTTP_SERVER_NAME is not set in settings, skip http nginx conf creation'))

        if nginx_context['NGINX_WEBSOCKET_SERVER_NAME']:
            with open(websocket_conf_filename, 'w') as f:
                f.write(render_to_string('conf/nginx/default-websocket.conf', context=nginx_context))
                self.stdout.write(self.style.SUCCESS(f'written Nginx websocket conf to {websocket_conf_filename}'))
        else:
            self.stderr.write(self.style.WARNING(
                'NGINX_WEBSOCKET_SERVER_NAME is not set in settings, skip websocket nginx conf creation'))

    def action_create(self, *args, **options):
        self.prepare_configuration_files()
