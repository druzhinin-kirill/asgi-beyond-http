"""ASGI application (TCP) for telemetry."""

from framework.main import Telematica
from framework.utils import AVLData, AVLDataResponse, Login

from application import data

app = Telematica()


@app.login()
async def login(login: Login):
    print(login)
    data.counter += 1
    return "Hello, world!"


@app.avl()
async def avl(avldata: AVLData):
    print(avldata)
    data.counter += 1
    return AVLDataResponse(avldata.record_count)


