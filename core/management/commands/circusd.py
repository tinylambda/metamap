import os
import subprocess
from typing import List

from django.conf import settings
from django.core.management.base import CommandError

from core.management.commands._base import MetaCommand


class Command(MetaCommand):
    help = "Manage the circusd service"

    def add_arguments(self, parser):
        parser.add_argument("action", nargs="?", help="specify the action you want to run", type=str)
        parser.add_argument('action_parameters', nargs="*", help="action parameters", type=str)

    @classmethod
    def prepare_configuration_files(cls):
        conf_filename = getattr(settings, "CIRCUSD_CONF_FILENAME", None)
        if conf_filename is None:
            raise CommandError("settings.CIRCUSD_CONF_FILENAME not specified")

        log_root_path = getattr(settings, "CIRCUSD_LOG_ROOT_DIR", None)
        if log_root_path is None:
            raise CommandError("settings.CIRCUSD_LOG_ROOT_DIR not specified")

        conf_dirname = os.path.dirname(conf_filename)
        if not os.path.exists(conf_dirname):
            os.makedirs(conf_dirname)

        if not os.path.exists(log_root_path):
            os.makedirs(log_root_path)

        with open(conf_filename, 'w') as f:
            settings.CIRCUSD_CONFIG.write(f)

    @classmethod
    def run_circusctl_cmd(cls, cmd_name=None, action_parameters: List[str] = None):
        circus_static_conf_list = getattr(settings, 'CIRCUSD_STATIC_CONFIG_LIST')
        circus_section = None
        for item in circus_static_conf_list:
            if item['name'] == 'circus':
                circus_section = item
        circus_section_settings = circus_section['settings']
        circus_endpoint = circus_section_settings['endpoint']
        cmd = ["circusctl"]
        cmd.extend(['--endpoint', circus_endpoint])
        if cmd_name:
            cmd.append(cmd_name)
            cmd.extend(action_parameters if action_parameters is not None else [])
        try:
            subprocess.run(cmd)
        except KeyboardInterrupt:
            pass

    @classmethod
    def action_update_conf_file(cls, *args, **options):
        cls.prepare_configuration_files()

    @classmethod
    def action_start(cls, *args, **options):
        cls.prepare_configuration_files()
        conf_filename = getattr(settings, 'CIRCUSD_CONF_FILENAME', None)
        cmd = ["circusd"]
        cmd.extend(['--daemon'])
        circusd_logfile = os.path.join(getattr(settings, 'CIRCUSD_LOG_ROOT_DIR', '/tmp/'), 'circusd.log')
        cmd.extend(['--log-output', circusd_logfile])
        cmd.extend([conf_filename])
        try:
            subprocess.run(cmd)
        except KeyboardInterrupt:
            pass

    @classmethod
    def action_stop(cls, *args, **options):
        cls.run_circusctl_cmd('quit')

    @classmethod
    def action_shell(cls, *args, **options):
        cls.run_circusctl_cmd()

    @classmethod
    def action_status(cls, *args, **options):
        action_parameters = options.get('action_parameters', [])
        cls.run_circusctl_cmd('stats', action_parameters)

    @classmethod
    def action_reload(cls, *args, **options):
        action_parameters = options.get('action_parameters', [])
        cls.run_circusctl_cmd('reload', action_parameters)
