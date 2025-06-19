"""ASGI applications."""

from framework.main import Telematica
from framework.utils import AVLData, AVLDataResponse, Login

from nicegui import ui, APIRouter, App

tcp_app = Telematica()
http_app = App()
http_router = APIRouter()

counter = 0


@tcp_app.login()
async def login(data: Login):
    global counter
    counter += 1
    return "Hello, world!"


@tcp_app.avl()
async def avl(data: AVLData):
    print(data)
    global counter
    counter += 1
    return AVLDataResponse(data.record_count)


@http_router.page("/login")
def index():
    ui.label("Hi")
    ui.label(str(counter))


http_app.include_router(http_router)
ui.run_with(http_app)
