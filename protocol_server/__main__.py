"""Start protocol server."""

import asyncio
import importlib
import logging
import sys
from pathlib import Path

import uvicorn

from protocol_server.server import TeltonikaProtocol

LOGGER = logging.getLogger("server")


def load_app(module_app: str):
    """Load ASGI application from a given path.

    The path has the pattern MODULE_NAME:APP to let
    the protocol server find and import ASGI application.
    """
    module, app_name = module_app.split(":")

    # Determine the module path to import application module.
    module_path = Path(module).resolve()
    sys.path.insert(0, str(module_path.parent))
    if module_path.is_file():
        import_name = module_path.with_suffix("").name
    else:
        import_name = module_path.name
    imported_module = importlib.import_module(import_name)

    app = eval(app_name, vars(imported_module))
    return app


async def get_tcp_server(tcp_app):
    host, port = "127.0.0.1", 8081
    loop = asyncio.get_running_loop()
    server = await loop.create_server(lambda: TeltonikaProtocol(tcp_app), host, port)
    return server


async def main():
    logging.basicConfig(level=logging.DEBUG)

    # Load ASGI applications.
    tcp_app = load_app("application.telematica:app")
    config = uvicorn.Config("application.web:app")

    # Initialize servers.
    http_server = uvicorn.Server(config)
    tcp_server = await get_tcp_server(tcp_app)

    # Run servers.
    LOGGER.info("Starting TCP and HTTP servers...")
    await asyncio.gather(http_server.serve(), tcp_server.serve_forever())


if __name__ in {"__main__"}:
    asyncio.run(main())
