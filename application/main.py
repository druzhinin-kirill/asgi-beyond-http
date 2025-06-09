"""App to handle vehicle sent data."""

from framework.main import Fastonika
from framework.utils import AVLData, AVLDataResponse, Login

app = Fastonika()


@app.login()
async def login(data: Login):
    print(data)
    return "Hello, world!"


@app.avl()
async def avl(data: AVLData):
    print(data)
    return AVLDataResponse(data.record_count)
