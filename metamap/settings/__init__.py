import os
import logging
import importlib

from .defaults import *

DJANGO_RUNTIME_ENV = os.environ.get('DJANGO_RUNTIME_ENV', 'dev')
print(f"__init__ DJANGO_RUNTIME_ENV:{DJANGO_RUNTIME_ENV}")
logging.info(f'NOTE: Running in environment {DJANGO_RUNTIME_ENV}')

module = f'{MAIN_MODULE_NAME}.settings.{DJANGO_RUNTIME_ENV}'
module_object = importlib.import_module(module)

globals().update(module_object.__dict__)
