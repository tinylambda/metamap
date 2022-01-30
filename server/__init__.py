import asyncio
import json
import logging
import os.path
import socket
import uuid

import aetcd3
import attr
import zmq.asyncio
from aetcd3 import Event
from django.conf import settings


class ServerRoutineMeta(type):
    """
    SERVER CORE LOOP: INPUT => LOGIC => OUTPUT
    """
    BASE_NAME = 'ServerRoutine'

    def __new__(mcs, name, bases, class_dict: dict):
        server_type = class_dict.get('SERVER_TYPE')
        if name != mcs.BASE_NAME and server_type is None:
            raise AttributeError('a server routine must specify SERVER_TYPE at class level')
        cls = type.__new__(mcs, name, bases, class_dict)
        return cls

    @property
    def host_ip(cls):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            ip = s.getsockname()[0]
        except Exception as e:
            logging.debug('Error when try to get local ip address', exc_info=e)
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip

    def __init__(cls, name, bases, class_dict: dict):
        cls.ASYNCIO_LOOP: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        cls.SD_EVENTS_BUFFER: list[Event] = []
        cls.SERVICE_ZMQ_CONTEXT = zmq.asyncio.Context()
        cls.SERVICE_SOCKET = cls.SERVICE_ZMQ_CONTEXT.socket(zmq.REP)
        cls.SERVICE_HOST = cls.host_ip
        cls.SERVICE_PORT = cls.SERVICE_SOCKET.bind_to_random_port('tcp://*',
                                                                  min_port=49152,
                                                                  max_port=65535,
                                                                  max_tries=64)
        cls.SERVICE_LOCK = os.path.join(settings.SERVICE_LOCK_ROOT, name)
        cls.SERVICE_REGISTER_KEY = os.path.join(settings.SERVICE_ROOT, name, uuid.uuid4().hex)
        cls.SERVICE_REGISTER_VALUE = json.dumps({
            'host_ip': cls.SERVICE_HOST,
            'port': cls.SERVICE_PORT,
        })
        cls.SERVICE_LEASE_SECONDS = settings.SERVICE_LEASE_SECONDS
        cls.SERVICE_LEASE_REFRESH_INTERVAL_SECONDS = settings.SERVICE_LEASE_REFRESH_INTERVAL_SECONDS
        cls.SERVICE_CLIENTS = {}

        cls.EVENT_SERVICE_STOP = asyncio.Event()
        cls.EVENT_FOUND_SELF = asyncio.Event()
        cls.EVENT_LOOP_STARTED = asyncio.Event()
        cls.EVENT_LISTEN_SERVICE_STARTED = asyncio.Event()

        cls.QUEUE_INPUT = asyncio.Queue()
        cls.QUEUE_OUTPUT = asyncio.Queue()

        super(ServerRoutineMeta, cls).__init__(name, bases, class_dict)

    def service_client(cls, host_ip, port, **kwargs):
        instance = cls.SERVICE_ZMQ_CONTEXT.socket(zmq.REQ)
        instance.connect(f'tcp://{host_ip}:{port}')
        return instance


@attr.s
class ServerRoutine(metaclass=ServerRoutineMeta):
    """
    Service discovery flow:
    1. Service A start. CHANGE_STATE: registering
    2. A acquire service registration lock to prevent other service registering.
    3. A start a task to listen changes of the service directory, if any events and state is registering, buffer them.
    4. A get all the registered services from related service directory, let's say 5 registered services now
    5. A create a CountDownLatch(5) condition.
    5. A start main loop to listen on some socket with the CountDownLatch(5) condition, count_down if any ping message.
    6. A wait on a CountDownLatch(5) to wait for 5 registered services to ping A
    7. If CountDownLatch(5), CHANGE_STATE: registered
    8. Apply the buffered events to put A to available services.
    9. The following events will apply as normal to maintain the latest services
    """
    service_ready_event = attr.ib(default=attr.Factory(asyncio.Event))
    zmq_context = attr.ib(default=attr.Factory(zmq.asyncio.Context))

    def __attrs_post_init__(self):
        self.socket = self.zmq_context.socket(zmq.REP)
        self.selected_port = self.socket.bind_to_random_port('tcp://*', min_port=49152, max_port=65535, max_tries=64)

        unique_id = uuid.uuid4().hex
        self.service_key = os.path.join(self.service_directory, unique_id)

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
            logging.debug('Error when try to get local ip address', exc_info=e)
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip

    async def register_self(self):
        async with aetcd3.client(**settings.ETCD_KWARGS) as client:
            async with client.lock(self.service_lock):
                async for value, metadata in client.get_prefix(self.service_directory):
                    self.__class__.SERVICES[metadata.key] = value

    def add_service(self, key: bytes, value):
        pass

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
