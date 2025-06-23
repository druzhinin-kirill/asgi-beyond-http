"""ASGI application (HTTP) for UI."""

import asyncio

from nicegui import ui, APIRouter, App

from application.data import records, vehicle

app = App()
router = APIRouter()


MAP_CENTER = (52.50, 13.350)


@router.page("/")
async def index():
    m = ui.leaflet(center=MAP_CENTER)
    marker = m.marker(latlng=m.center)

    logs = ui.log()
    ui.timer(1.0, lambda: marker.move(vehicle.lat, vehicle.lng))

    async def show_logs():
        _record = await records.get()
        logs.push(_record)

        while True:
            record = await records.get()
            logs.push(_record)
            m.generic_layer(
                name="polyline",
                args=[
                    [
                        [_record.latitude, _record.longitude],
                        [record.latitude, record.longitude],
                    ],
                    {"color": "red", "weight": 3},
                ],
            )
            _record = record

    asyncio.create_task(show_logs())


app.include_router(router)
ui.run_with(app)
