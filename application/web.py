"""ASGI application (HTTP) for UI."""

from nicegui import ui, APIRouter, App

from application import data

app = App()
router = APIRouter()


@router.page("/login")
def index():
    ui.label("Hi")
    ui.label(data.counter)


app.include_router(router)
ui.run_with(app)
