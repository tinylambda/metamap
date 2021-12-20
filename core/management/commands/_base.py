import logging

from django.core.management.base import BaseCommand, CommandError


class MetaCommand(BaseCommand):
    def handle(self, *args, **options):
        supported_actions = [item.replace('action_', '')
                             for item in dir(self)
                             if item.startswith('action_')]
        action = options['action']
        if not action:
            raise CommandError(f'Please specify the action, supported actions: {",".join(supported_actions)}')
        action_method_name = f"action_{action}"

        try:
            getattr(self, action_method_name)(*args, **options)
        except AttributeError as e:
            logging.debug('MetaCommand handle error', exc_info=e)
            raise CommandError(f'Unsupported action {action}, supported actions: {",".join(supported_actions)}') from e

        self.stdout.write(self.style.SUCCESS("Done"))
