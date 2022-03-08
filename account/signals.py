import logging

from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver


logger = logging.getLogger('django')


@receiver(user_logged_in)
def user_logged_in_handle(sender, user, **kwargs):
    logger.info('signal user_logged_in, %s, %s', sender, user)


@receiver(user_logged_out)
def user_logged_out_handle(sender, user, **kwargs):
    logger.info('signal user_logged_out, %s, %s', sender, user)


@receiver(user_login_failed)
def user_login_failed_handle(sender, **kwargs):
    logger.info('signal user_login_failed, %s, %s', sender, kwargs)
