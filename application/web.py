"""ASGI application (HTTP) for UI."""

import asyncio

from nicegui import ui, APIRouter, App

from application.data import records, vehicle

app = App()
router = APIRouter()


MAP_CENTER = (52.50, 13.350)


@router.page("/")
async def index():
    ui.label.default_classes("text-gray-900")
    ui.card.default_classes("col text-center")
    ui.card.default_props("flat bordered")

    with ui.grid(rows="1fr 3fr").classes("w-11/12 place-self-center h-screen"):
        with ui.column(align_items="center").classes(
            "mt-4 text-center w-5/6 place-self-center"
        ):
            ui.label("Breaking HTTP Boundaries").classes("text-h2 font-bold")
            ui.label("ASGI to build a fleet management system in Python").classes(
                "mb-4 text-h4"
            )

        with ui.row(align_items="stretch").classes("mb-4"):
            with ui.card(align_items="center"):
                ui.label("Map").classes("text-h4")
                m = ui.leaflet(center=MAP_CENTER).classes("h-full container")
                marker = m.marker(latlng=m.center)

            with ui.card(align_items="center"):
                ui.label("Live Logs").classes("text-h4")
                logs = ui.log().classes("h-96 container")

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
