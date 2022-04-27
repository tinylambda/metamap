from ninja import NinjaAPI
from ninja_extra import NinjaExtraAPI, api_controller, http_get


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


api_extra.register_controllers(MathAPI)
