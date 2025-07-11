"""ASGI application (HTTP) for UI."""

import asyncio

from nicegui import ui, APIRouter, App

from application.data import records, vehicle

app = App()
router = APIRouter()

ui.label.default_classes("text-gray-900")
ui.card.default_classes("col text-center")
ui.card.default_props("flat bordered")

MAP_CENTER = (50.077019, 14.475541)


@router.page("/")
async def index():
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

            with ui.card(align_items="center"):
                ui.label("Live Logs").classes("text-h4")
                logs = ui.log().classes("h-96 container justify-items-start")

    async def track_vehicle():
        _record = await records.get()
        logs.push(_record.text)
        marker = m.marker(latlng=vehicle.position)

        while True:
            record = await records.get()
            logs.push(_record.text)
            marker.move(vehicle.lat, vehicle.lng)

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

    asyncio.create_task(track_vehicle())


app.include_router(router)
ui.run_with(app)
