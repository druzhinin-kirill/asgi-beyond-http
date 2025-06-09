"""Start protocol server."""

import asyncio
import importlib
import logging
import sys
from pathlib import Path

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


async def main():
    """Start ASGI server for Teltonika.

    Load application and start server on localhost:8081.
    """
    app = load_app(sys.argv[-1])
    host, port = "127.0.0.1", 8081
    logging.basicConfig(level=logging.DEBUG)

    loop = asyncio.get_running_loop()
    server = await loop.create_server(lambda: TeltonikaProtocol(app), host, port)
    LOGGER.info("Server started at {}:{}".format(host, port))

    await server.serve_forever()


asyncio.run(main())
