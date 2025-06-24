"""ASGI application (TCP) for telemetry."""

from framework.main import Telematica
from framework.utils import AVLData, AVLDataResponse, Login

from application.data import vehicle, records

app = Telematica()


@app.login()
async def login(login: Login):
    """Handle incoming login packets."""
    print(login)
    return "Hello, world!"


@app.avl()
async def avl(avldata: AVLData):
    """Handle incoming data packets."""
    for record in avldata.records:
        records.put_nowait(record)
        vehicle.lat, vehicle.lng = record.latitude, record.longitude
    return AVLDataResponse(avldata.record_count)
