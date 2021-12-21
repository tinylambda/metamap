import asyncio
import json
import signal
import sys
from typing import Callable

import attr
import websockets
from websockets.legacy.protocol import WebSocketCommonProtocol


@attr.s
class WebsocketClient:
    uri = attr.ib(type=str)
    extra_headers = attr.ib(type=list[tuple[str, str]], default=attr.Factory(list))
    on_open = attr.ib(type=Callable, default=None)
    on_message = attr.ib(type=Callable, default=None)
    on_error = attr.ib(type=Callable, default=None)
    input_q = attr.ib(type=asyncio.Queue, init=False)
    event_loop = attr.ib(type=asyncio.BaseEventLoop, init=False)
    ws: WebSocketCommonProtocol = attr.ib(init=False)

    def __attrs_post_init__(self):
        self.input_q = asyncio.Queue()
        self.event_loop = asyncio.get_event_loop()
        self.waiting_tasks: dict[str, asyncio.Task] = {}

        signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
        for s in signals:
            self.event_loop.add_signal_handler(s, lambda s=s: asyncio.create_task(
                self.shutdown(loop=self.event_loop, sig=s)))

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

    async def shutdown(self, loop: asyncio.BaseEventLoop, sig=None):
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        [task.cancel() for task in tasks]
        await asyncio.gather(*tasks, return_exceptions=True)
        await self.ws.close()
        loop.stop()

    def get_input_task(self) -> asyncio.Task:
        return self.event_loop.create_task(self.input_q.get())

    def get_recv_task(self, client_side_ws) -> asyncio.Task:
        return self.event_loop.create_task(client_side_ws.recv())

    def refresh_tasks(self):
        input_task: asyncio.Task = self.waiting_tasks.get('input_task')
        if input_task is None or input_task.done():
            self.waiting_tasks.update({'input_task': self.get_input_task()})

        recv_task: asyncio.Task = self.waiting_tasks.get('recv_task')
        if recv_task is None or recv_task.done():
            self.waiting_tasks.update({'recv_task': self.get_recv_task(self.ws)})

    async def _run(self):
        async with websockets.connect(self.uri, extra_headers=self.extra_headers) as client_side_ws:
            self.do_callback(self.on_open)
            self.ws = client_side_ws
            while True:
                try:
                    self.refresh_tasks()
                    await asyncio.wait(self.waiting_tasks.values(), return_when=asyncio.FIRST_COMPLETED)

                    input_task: asyncio.Task = self.waiting_tasks['input_task']
                    if input_task.done():
                        e: dict = input_task.result()
                        value = e.get('value')
                        data_dict = {
                            'message': value
                        }
                        data_json = json.dumps(data_dict)
                        data_bytes = data_json.encode('utf-8')
                        await client_side_ws.send(data_bytes)

                    recv_task: asyncio.Task = self.waiting_tasks['recv_task']
                    if recv_task.done():
                        data = recv_task.result()
                        self.do_callback(self.on_message, data)
                        data_dict: dict = json.loads(data)
                        message: str = data_dict.get('message')
                        if message.strip() == 'bye':
                            print('bye bye')
                            break
                except Exception as e:
                    self.do_callback(self.on_error, e)

    def run(self):
        try:
            self.event_loop.add_reader(sys.stdin, self.get_stdin, self.input_q)
            self.event_loop.create_task(self._run())
            self.event_loop.run_forever()
        finally:
            self.event_loop.close()
            print('bye')

    async def run_with_retry(self):
        pass


if __name__ == '__main__':
    client = WebsocketClient('ws://localhost:8000/ws/access/cc/',
                             on_message=lambda msg: print(msg),
                             on_error=lambda e: print(e),)
    client.run()
