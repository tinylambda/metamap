import argparse
import asyncio
import json
import logging
import signal
import sys
import time
from typing import Callable
from urllib.parse import urljoin, urlencode, parse_qsl, urlunsplit

import attr
import websockets
from websockets.exceptions import ConnectionClosedError
from websockets.legacy.protocol import WebSocketCommonProtocol


@attr.s
class WebsocketClient:
    CONN_TRIED_TIMES = 0

    uri = attr.ib(type=str)
    extra_headers = attr.ib(type=list[tuple[str, str]], default=attr.Factory(list))
    on_open = attr.ib(type=Callable, default=None)
    on_message = attr.ib(type=Callable, default=None)
    on_error = attr.ib(type=Callable, default=None)
    on_close = attr.ib(type=Callable, default=None)
    input_q = attr.ib(type=asyncio.Queue, init=False)
    event_loop = attr.ib(default=None, type=asyncio.BaseEventLoop, init=False)
    ws = attr.ib(type=WebSocketCommonProtocol, default=None, init=False)
    ws_recv_task = attr.ib(type=asyncio.Task, default=None, init=False)
    user_input_task = attr.ib(type=asyncio.Task, default=None, init=False)
    shutdown_signal = attr.ib(default=None, init=False)
    shutdown_reason = attr.ib(type=str, default=None, init=False)

    def __attrs_post_init__(self):
        self.server_close_message = 'server close the connection'
        self.input_q = asyncio.Queue()
        self.event_loop = asyncio.get_event_loop()
        signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
        for s in signals:
            self.event_loop.add_signal_handler(
                s,
                lambda _s=s: asyncio.create_task(
                    self.shutdown(loop=self.event_loop, sig=_s)
                ),
            )
        self.event_loop.set_exception_handler(self.handle_exception)

    @staticmethod
    def do_callback(f: Callable, *args, **kwargs):
        if f is not None:
            f(*args, **kwargs)

    @staticmethod
    def get_stdin(eq: asyncio.Queue):
        e = {
            'type': 'stdin',
            'value': sys.stdin.readline(),
        }
        asyncio.ensure_future(eq.put(e))

    def shutdown_normal(self):
        return self.shutdown_signal is not None

    async def shutdown(self, loop: asyncio.AbstractEventLoop, sig=None, reason=None):
        self.shutdown_signal = sig
        self.shutdown_reason = reason
        logging.warning(
            'shutdown with signal=%s and reason=%s',
            self.shutdown_signal,
            self.shutdown_reason,
        )

        try:
            tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
            [task.cancel() for task in tasks]
            await asyncio.gather(*tasks, return_exceptions=True)
            if self.ws is not None:
                await self.ws.close()
        except Exception as e:
            logging.warning(
                'shutdown encounter an error, find the root cause and fix it asap',
                exc_info=e,
            )
        finally:
            loop.stop()

    def get_input_task(self) -> asyncio.Task:
        return self.event_loop.create_task(self.input_q.get())

    def get_recv_task(self) -> asyncio.Task:
        return self.event_loop.create_task(self.ws.recv())

    def handle_exception(self, loop, context):
        msg = context.get('exception', context['message'])
        self.shutdown_reason = msg
        if isinstance(msg, ConnectionClosedError):
            msg = self.server_close_message
        asyncio.create_task(self.shutdown(loop=loop, reason=msg))

    async def handle_user_input(self):
        if self.user_input_task.done():
            event: dict = self.user_input_task.result()
            value = event.get('value')
            data_dict = {'message': value}
            data_json = json.dumps(data_dict)
            data_bytes = data_json.encode('utf-8')
            await self.ws.send(data_bytes)
            # schedule a new input task
            self.user_input_task = self.get_input_task()

    async def handle_ws_recv(self):
        if self.ws_recv_task.done():
            exception = self.ws_recv_task.exception()
            if exception is not None and isinstance(exception, ConnectionClosedError):
                self.do_callback(self.on_close, exception)
                raise exception

            data = self.ws_recv_task.result()
            data_dict: dict = json.loads(data)
            self.do_callback(self.on_message, data_dict)
            # schedule a new recv task
            self.ws_recv_task = self.get_recv_task()

    async def _run(self):
        async with websockets.connect(
            self.uri, extra_headers=self.extra_headers
        ) as client_side_ws:
            # increment connect tried times
            self.__class__.CONN_TRIED_TIMES = 0

            self.do_callback(self.on_open)
            self.ws = client_side_ws
            self.ws_recv_task = self.get_recv_task()
            self.user_input_task = self.get_input_task()

            while True:
                await asyncio.wait(
                    [self.ws_recv_task, self.user_input_task],
                    return_when=asyncio.FIRST_COMPLETED,
                )
                await self.handle_user_input()
                await self.handle_ws_recv()

    def run(self):
        self.event_loop.add_reader(sys.stdin, self.get_stdin, self.input_q)
        self.event_loop.create_task(self._run())
        self.event_loop.run_forever()

    @classmethod
    def start(
        cls,
        uri=None,
        on_open=None,
        on_message=None,
        on_error=None,
        on_close=None,
        **kwargs,
    ):
        client = cls(
            uri=uri,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            **kwargs,
        )
        client.run()
        return client.shutdown_normal()

    @classmethod
    def start_with_retry(cls, *args, **kwargs):
        try:
            max_retry_times = kwargs.pop('max_retry_times')
        except KeyError:
            max_retry_times = 10

        while True:
            cls.CONN_TRIED_TIMES += 1
            shutdown_normal = cls.start(*args, **kwargs)
            if shutdown_normal or cls.CONN_TRIED_TIMES > max_retry_times:
                break
            else:
                logging.warning('Reconnecting')
                time.sleep(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--host', action='store', dest='host', type=str, default='localhost'
    )
    parser.add_argument('--port', action='store', dest='port', type=int, default=8000)
    parser.add_argument(
        '--path', action='store', dest='path', type=str, default='/ws/access/'
    )
    parser.add_argument(
        '--group', action='store', dest='group', type=str, default='defaultGroup/'
    )
    parser.add_argument(
        '--query-args', action='store', dest='query_args', type=str, default=''
    )
    parser.add_argument('--use-ssl', action='store_true', dest='use_ssl', default=False)
    ns = parser.parse_args()

    scheme = 'wss' if ns.use_ssl else 'ws'
    netloc = f'{ns.host}:{ns.port}'
    path = urljoin(ns.path, ns.group)
    if ns.query_args:
        query = urlencode(parse_qsl(ns.query_args))
    else:
        query = ''
    fragment = ''
    uri = urlunsplit((scheme, netloc, path, query, fragment))
    logging.warning('Connect to %s', uri)
    WebsocketClient.start_with_retry(
        uri=uri,
        on_open=lambda: print('connected'),
        on_message=lambda msg: print(f'--{msg}--'),
        on_error=lambda e: print(e),
        on_close=lambda e: print('on_close: bye'),
        max_retry_times=10000,
    )

    # python core/utils/ws_client.py --query-args 'a=100&b=200'
