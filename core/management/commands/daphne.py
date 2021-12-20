import multiprocessing
import os
import signal
import subprocess

from django.core.management.base import CommandError

from core.management.commands._base import MetaCommand


class Command(MetaCommand):
    help = 'Manage the Daphne ASGI service'
    P = None

    def add_arguments(self, parser):
        parser.add_argument("action", nargs="?", help="specify the action you want to run", type=str)
        parser.add_argument(
            '--bind', dest='bind', default='0.0.0.0',
            help='Listening host',
        )
        parser.add_argument(
            '--port', dest='port', default='20000',
            help='Listening port'
        )
        parser.add_argument(
            '--fd', dest='fd',
            help='Use a existing socket'
        )
        parser.add_argument(
            '--endpoint', dest='endpoint',
            help='Control over the port/socket bindings'
        )
        parser.add_argument(
            '--app', dest='app',
            help='The app to run'
        )

    @classmethod
    def prepare_configuration_files(cls):
        pass

    @staticmethod
    def send_signal_to_process(pid, sig_number):
        os.kill(pid, sig_number)

    @classmethod
    def action_start(cls, *args, **options):
        def handle_quit_signal(signum, stack):
            # We must execute this action in a separate process.
            p = multiprocessing.Process(target=cls.send_signal_to_process, args=(cls.P.pid, signal.SIGINT))
            p.start()
            p.join()

        signal.signal(signal.SIGQUIT, handle_quit_signal)
        signal.signal(signal.SIGINT, handle_quit_signal)

        cls.prepare_configuration_files()

        daphne_application = options['app']
        if daphne_application is None:
            raise CommandError('Please specify the app daphne to run. use --app APP_NAME')

        fd = options['fd']
        if fd:
            cmd = ['daphne', '--fd', fd]
        else:
            bind = options['bind']
            port = options['port']
            cmd = ['daphne', '--bind', bind, '--port', port]

        endpoint = options['endpoint']
        if endpoint:
            cmd.extend(['--endpoint', endpoint])

        cmd.append(daphne_application)

        try:
            # subprocess.run(cmd)
            # close_fds should be False, won't close the socket inherit from the parent process.
            cls.P = subprocess.Popen(cmd, close_fds=False)
            cls.P.wait()
        except KeyboardInterrupt:
            pass
