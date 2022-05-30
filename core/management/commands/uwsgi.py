import os
import signal
import subprocess
from configparser import NoOptionError

from django.conf import settings
from django.core.management.base import CommandError

from core.management.commands._base import MetaCommand


class Command(MetaCommand):
    help = "Manage uWSGI service"

    def add_arguments(self, parser):
        parser.add_argument(
            "action", nargs="?", help="specify the action you want to run", type=str
        )

    @classmethod
    def prepare_configuration_files(cls):
        uwsgi_conf_filename = getattr(settings, 'UWSGI_CONF_FILENAME', None)
        if uwsgi_conf_filename is None:
            raise CommandError("settings.UWSGI_CONF_FILENAME not specified")

        uwsgi_conf_dirname = os.path.dirname(uwsgi_conf_filename)
        if not os.path.exists(uwsgi_conf_dirname):
            os.makedirs(uwsgi_conf_dirname)

        with open(uwsgi_conf_filename, 'w') as f:
            settings.UWSGI_CONFIG.write(f)

    @classmethod
    def action_start(cls, *args, **options):
        def handle_quit_signal(signum, stack):
            try:
                pidfile = settings.UWSGI_CONFIG.get('uwsgi', 'pidfile')
                subprocess.call(["uwsgi", "--stop", f"{pidfile}"])
            except KeyboardInterrupt:
                pass

        # SIGQUIT/SIGINT will trigger `uwsgi --stop <uwsgi_pidfile>` command (see above)
        # (immediately kill the entire uWSGI stack)
        signal.signal(signal.SIGQUIT, handle_quit_signal)
        signal.signal(signal.SIGINT, handle_quit_signal)

        cls.prepare_configuration_files()
        cmd = ["uwsgi", "--ini", settings.UWSGI_CONF_FILENAME]
        try:
            subprocess.run(cmd)
        except KeyboardInterrupt:
            pass

    @classmethod
    def action_stop(cls, *args, **options):
        try:
            pidfile = settings.UWSGI_CONFIG.get('uwsgi', 'pidfile')
        except NoOptionError:
            pidfile = None

        if pidfile is not None and os.path.exists(pidfile):
            cmd = ["uwsgi", "--stop", f"{pidfile}"]
            try:
                subprocess.run(cmd)
            except KeyboardInterrupt:
                pass
        else:
            raise CommandError(
                "Cannot find the PID file of uWSGI server, is the server running?"
            )

    @classmethod
    def action_reload(cls, *args, **options):
        try:
            touch_chain_reload = settings.UWSGI_CONFIG.get(
                "uwsgi", "touch-chain-reload"
            )
        except NoOptionError:
            touch_chain_reload = None

        if touch_chain_reload is not None:
            cmd = ["touch", f"{touch_chain_reload}"]
        else:
            pidfile = getattr(settings, "UWSGI_PIDFILE", None)
            if pidfile is not None and os.path.exists(pidfile):
                cmd = ["uwsgi", "--reload", f"{pidfile}"]
            else:
                raise CommandError("Cannot find the PID file of uWSGI server")
        try:
            subprocess.run(cmd)
        except KeyboardInterrupt:
            pass

    @classmethod
    def action_status(cls, *args, **options):
        try:
            stats_server_config = settings.UWSGI_CONFIG.get("uwsgi", "stats")
            stats_server_config = stats_server_config.replace("0.0.0.0", "127.0.0.1")
        except NoOptionError:
            stats_server_config = None

        if stats_server_config is not None:
            try:
                stats_server_config_http = f"http://{stats_server_config}"
                cmd = ["uwsgitop", stats_server_config_http]
                p = subprocess.Popen(cmd, shell=False, start_new_session=True)
                p.wait()
            except KeyboardInterrupt:
                os.kill(p.pid, signal.SIGINT)
            except subprocess.CalledProcessError as e:
                pass
            finally:
                pass
        else:
            raise CommandError("No stats server configured for this uWSGI instance.")
