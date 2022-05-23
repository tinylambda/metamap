from typing import List, Optional

from ninja import NinjaAPI, Schema, Query
from ninja_extra import NinjaExtraAPI, api_controller, http_get, http_post
from pydantic import Field

from server.models import Server

api = NinjaAPI(version='2.0.0')
api_extra = NinjaExtraAPI()


@api.get('/hello')
def hello(request):
    return 'Hello world'


@api_extra.get('/add', tags=['Math', 'important'])
def add(request, a: int, b: int):
    return {'result': a + b}


@api_extra.get('/add_float', tags=['Math', 'important'])
def add_float(request, a: float, b: float):
    return {'result': a + b}


@api_controller('/', tags=['Math'], permissions=[])
class MathAPI:
    @http_get('/substract')
    def substract(self, a: int, b: int):
        return {'result': a - b}

    @http_get('/divide')
    def divide(self, a: int, b: int):
        return {'result': a / b}

    @http_get('/multiple')
    def multiple(self, a: int, b: int):
        return {'result': a * b}


class CreateServerArgs(Schema):
    name: str = Field(...)
    ip: str = Field()


class SearchServerArgs(Schema):
    name: str = Field()
    city: Optional[str] = Field()


class SearchServerSortArgs(Schema):
    field: str = Field(default='id')
    order: str = Field(default='ASC')


class ServerItem(Schema):
    name: str = Field(...)


@api_controller('/server', tags=['Server'])
class ServerAPI:
    @http_post('/create_server', response=CreateServerArgs)
    def create_server(
        self,
        request,
        create_server_args: CreateServerArgs = Query(None),
    ):
        return create_server_args

    @http_get('/search_server', response=List[ServerItem])
    def search_server(
        self,
        request,
        search_args: SearchServerArgs = Query(None),
        sort_args: SearchServerSortArgs = Query(None),
    ):
        servers = [
            Server(name=f's{item}', ip=f'192.168.0.{item}') for item in range(10)
        ]
        return servers


api_extra.register_controllers(MathAPI)
api_extra.register_controllers(ServerAPI)
