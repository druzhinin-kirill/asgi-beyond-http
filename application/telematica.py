"""ASGI application (TCP) for telemetry."""

from framework.main import Telematica
from framework.utils import AVLData, AVLDataResponse, Login

from application.data import vehicle, records

app = Telematica()

KNOWN_VEHICLES = ["123456789012345"]


@app.login()
async def login(login: Login):
    """Handle incoming login packets."""
    if login.imei not in KNOWN_VEHICLES:
        raise ValueError("Invalid imei")


@app.avl()
async def avl(avldata: AVLData):
    """Handle incoming data packets."""
    for record in avldata.records:
        records.put_nowait(record)
        vehicle.lat, vehicle.lng = record.latitude, record.longitude
    return AVLDataResponse(avldata.record_count)
