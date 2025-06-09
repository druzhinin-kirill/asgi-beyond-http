"""Framework to build ASGI applications for Teltonika."""

from framework.utils import AVLData, Login


class Fastonika:
    """ASGI framework to build ASGI applications for Teltonika."""

    def __init__(self):
        self.handlers = {}

    async def __call__(self, scope, receive, send):
        """Process and dispatch ASGI events to corresponding handlers."""
        assert scope["type"] == "teltonika"
        event = await receive()

        match event.get("type"):
            case "teltonika.login":
                msg = Login.from_bytes(event["data"])
                try:
                    await self.handlers["login"](msg)
                    await send({"type": "teltonika.login.accept"})
                except Exception:
                    await send({"type": "teltonika.login.reject"})

            case "teltonika.avl":
                msg = AVLData.from_bytes(event["data"])
                processed_data = 0
                try:
                    resp = await self.handlers["avl"](msg)
                    processed_data = resp.num
                finally:
                    await send({"type": "teltonika.avl.accept", "data": processed_data})
            case _:
                raise Exception(f"unknown scope type: {scope}")

    def login(self):
        """Decorator that registers a handler for Login type"""

        def decorator(func):
            self.handlers["login"] = func
            return func

        return decorator

    def avl(self):
        """Decorator that registers a handler for AVL type"""

        def decorator(func):
            self.handlers["avl"] = func
            return func

        return decorator
