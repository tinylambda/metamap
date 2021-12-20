import importlib
import logging

from .defaults import *

DJANGO_RUNTIME_ENV = os.environ.get('DJANGO_RUNTIME_ENV', 'dev')
logging.info(f'NOTE: Running in environment {DJANGO_RUNTIME_ENV}')

module = f'{MAIN_MODULE_NAME}.settings.{DJANGO_RUNTIME_ENV}'
module_object = importlib.import_module(module)

globals().update(module_object.__dict__)
