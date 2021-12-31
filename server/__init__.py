import asyncio
import logging
import os.path
import socket
import threading
import uuid

import aetcd3
from django.conf import settings
from uhashring import HashRing


class ServerRoutineMeta(type):
    BASE_NAME = 'ServerRoutine'
    SERVICES_CACHE_NAME = 'SERVICES'
    HASH_RING_NAME = 'HASH_RING'

    def __new__(mcs, clsname, bases, class_dict: dict):
        server_type = class_dict.get('SERVER_TYPE')
        if clsname != mcs.BASE_NAME and server_type is None:
            raise AttributeError('a server routine must specify SERVER_TYPE at class leve')
        if mcs.SERVICES_CACHE_NAME not in class_dict:
            class_dict[mcs.SERVICES_CACHE_NAME] = []
        if mcs.HASH_RING_NAME not in class_dict:
            class_dict[mcs.HASH_RING_NAME] = HashRing(nodes=[])

        cls = type.__new__(mcs, clsname, bases, class_dict)
        return cls


class ServerRoutine(metaclass=ServerRoutineMeta):
    @classmethod
    def _attach_loop(cls):
        if threading.current_thread() is not threading.main_thread():
            logging.info('attaching loop in non-main thread')
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
        else:
            logging.info('use the default asyncio loop')

    @classmethod
    def _get_registry_prefix(cls):
        return os.path.join(settings.SERVICE_ROOT, cls.SERVER_TYPE)

    @classmethod
    def _get_service_lock_key(cls):
        return os.path.join(settings.SERVICE_LOCK_ROOT, cls.SERVER_TYPE)

    @classmethod
    def _get_ip(cls):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            ip = s.getsockname()[0]
        except Exception as e:
            logging.debug('error when try to get local ip address', exc_info=e)
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip

    def _generate_service_key(self):
        return f'{self.__class__.SERVER_TYPE}_{uuid.uuid4().hex}'

    @classmethod
    async def maintain_services(cls):
        watch_prefix = cls._get_registry_prefix()
        cls.SERVICES.clear()
        async with aetcd3.client(**settings.ETCD_KWARGS) as aetcd3_client:
            it, cancel = await aetcd3_client.watch_prefix(watch_prefix)
            async for event in it:
                logging.info('detected event: %s', event)

    @classmethod
    def run(cls):
        pass

    async def refresh_self(self):
        pass
