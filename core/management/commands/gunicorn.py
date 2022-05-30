import multiprocessing
import os
import signal
import subprocess

from django.conf import settings
from django.core.management.base import CommandError

from core.management.commands._base import MetaCommand


class Command(MetaCommand):
    help = 'Manage the Gunicorn WSGI service'
    P = None

    def add_arguments(self, parser):
        parser.add_argument(
            "action", nargs="?", help="specify the action you want to run", type=str
        )

    @classmethod
    def prepare_configuration_files(cls):
        gunicorn_conf_filename = getattr(settings, 'GUNICORN_CONFIG_FILENAME', None)
        if gunicorn_conf_filename is None:
            raise CommandError('settings.GUNICORN_CONFIG_FILENAME not specified')

        gunicorn_conf_content = getattr(settings, 'GUNICORN_CONFIG', None)
        if gunicorn_conf_content is None:
            raise CommandError('settings.GUNICORN_CONFIG not specified')

        gunicorn_conf_dirname = os.path.dirname(gunicorn_conf_filename)
        if not os.path.exists(gunicorn_conf_dirname):
            os.makedirs(gunicorn_conf_dirname)

        with open(gunicorn_conf_filename, 'w') as f:
            f.write(gunicorn_conf_content)

    @staticmethod
    def send_signal_to_process(pid, sig_number):
        os.kill(pid, sig_number)

    @classmethod
    def action_start(cls, *args, **options):
        def handle_quit_signal(signum, stack):
            # We must execute this action in a separate process.
            p = multiprocessing.Process(
                target=cls.send_signal_to_process, args=(cls.P.pid, signal.SIGINT)
            )
            p.start()
            p.join()

        signal.signal(signal.SIGQUIT, handle_quit_signal)
        signal.signal(signal.SIGINT, handle_quit_signal)

        cls.prepare_configuration_files()

        try:
            # subprocess.run(cmd)
            # close_fds should be False, won't close the socket inherit from the parent process.
            cmd = ['gunicorn', '--config', settings.GUNICORN_CONFIG_FILENAME]
            cls.P = subprocess.Popen(cmd, close_fds=False)
            cls.P.wait()
        except KeyboardInterrupt:
            pass
