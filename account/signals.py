# import logging
#
# from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
# from django.db.models.signals import pre_save
# from django.dispatch import receiver
#
# from account.models import User

# logger = logging.getLogger('django')
#
#
# @receiver(user_logged_in)
# def user_logged_in_handle(sender, user, **kwargs):
#     logger.info('signal user_logged_in, %s, %s, %s', sender, user, kwargs)
#
#
# @receiver(user_logged_out)
# def user_logged_out_handle(sender, user, **kwargs):
#     logger.info('signal user_logged_out, %s, %s, %s', sender, user, kwargs)
#
#
# @receiver(user_login_failed)
# def user_login_failed_handle(sender, **kwargs):
#     logger.info('signal user_login_failed, %s, %s', sender, kwargs)


# @receiver(request_started)
# def request_started_handle(sender, **kwargs):
#     scope = kwargs.get('scope', None)  # ASGI
#     environ = kwargs.get('environ', None)  # WSGI
#     logger.info('signal request_started, sender=%s, scope=%s, environ=%s, kwargs=%s', sender, scope, environ, kwargs)
#
#
# @receiver(request_finished)
# def request_finished_handle(sender, **kwargs):
#     logger.info('signal request_finished, sender=%s, kwargs=%s', sender, kwargs)


# @receiver(pre_save, sender=User)
# def pre_save_user(sender, instance, raw, using, update_fields, **kwargs):
#     logger.info('signal sender=%s, instance=%s, raw=%s, using=%s, update_fields=%s, kwargs=%s',
#                 sender, instance, raw, using, update_fields, kwargs)
