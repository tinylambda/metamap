import asyncio
import logging
import os.path
import socket
import threading
import uuid

import aetcd3
import attr
import zmq.asyncio
from django.conf import settings
from uhashring import HashRing


class ServerRoutineMeta(type):
    BASE_NAME = 'ServerRoutine'
    SERVICES_NAME = 'SERVICES'
    SERVICES_CANDIDATE_NAME = 'SERVICES_CANDIDATE'
    HASH_RING_NAME = 'HASH_RING'

    def __new__(mcs, clsname, bases, class_dict: dict):
        server_type = class_dict.get('SERVER_TYPE')

        if clsname != mcs.BASE_NAME and server_type is None:
            raise AttributeError('a server routine must specify SERVER_TYPE at class leve')

        if mcs.SERVICES_NAME not in class_dict:
            class_dict[mcs.SERVICES_NAME] = {}

        if mcs.SERVICES_CANDIDATE_NAME not in class_dict:
            class_dict[mcs.SERVICES_CANDIDATE_NAME] = {}

        if mcs.HASH_RING_NAME not in class_dict:
            class_dict[mcs.HASH_RING_NAME] = HashRing(nodes=[])

        cls = type.__new__(mcs, clsname, bases, class_dict)
        return cls


@attr.s
class ServerRoutine(metaclass=ServerRoutineMeta):
    service_ready_event = attr.ib(default=attr.Factory(asyncio.Event))
    zmq_context = attr.ib(default=attr.Factory(zmq.asyncio.Context))

    def __attrs_post_init__(self):
        self.socket = self.zmq_context.socket(zmq.REP)
        self.selected_port = self.socket.bind_to_random_port('tcp://*', min_port=49152, max_port=65535, max_tries=64)

        unique_id = uuid.uuid4().hex
        self.service_key = os.path.join(self.service_directory, unique_id)

        if threading.current_thread() is not threading.main_thread():
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)

    @property
    def service_directory(self):
        """Where to register this service instance"""
        return os.path.join(settings.SERVICE_ROOT, self.__class__.__name__)

    @property
    def service_lock(self):
        """Require this lock to register this type of service instances"""
        return os.path.join(settings.SERVICE_LOCK_ROOT, self.__class__.__name__)

    @property
    def host_ip(self):
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

    async def register_self(self):
        async with aetcd3.client(**settings.ETCD_KWARGS) as client:
            async with client.lock(self.service_lock):
                async for value, metadata in client.get_prefix(self.service_directory):
                    self.__class__.SERVICES[metadata.key] = value

    async def listen_service_changes(self):
        async with aetcd3.client(**settings.ETCD_KWARGS) as client:
            it, cancel = await client.watch_prefix(self.service_directory)
            async for event in it:
                pass

    async def refresh_self(self):
        pass

    async def action_ping(self):
        pass

    @classmethod
    def run(cls):
        pass
