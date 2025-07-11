"""Server implementation."""

import asyncio
import logging

from teltonika import (
    AcceptPacket,
    AckPacket,
    AVLPacket,
    LoginPacket,
    NeedMoreData,
    RejectPacket,
    Teltonika,
)
from teltonika.packets import CRC16CheckFailed

LOGGER = logging.getLogger(__name__)


class TeltonikaProtocol(asyncio.Protocol):
    """Implement protocol to handle incoming connections."""

    def __init__(self, app):
        self.connection = Teltonika()
        self.app = app
        self.event_queue = asyncio.Queue()

    def connection_made(self, transport):
        peername = transport.get_extra_info("peername")
        logging.debug("Connection from {}".format(peername))
        self.transport = transport

    def data_received(self, data):
        self.connection.receive_data(data)
        logging.debug("Raw data received: {}".format(data))
        self._deliver_events()

    def _deliver_events(self):
        """Process protocol events.

        NeedMoreData - Not enough data to handle. Skip processing.
        CRC16CheckFailed - Corrupted data received. Reject packet.
        AVLPacket | LoginPacket - Process packet.
        """
        while True:
            event = self.connection.next_event()
            match event:
                case NeedMoreData():
                    logging.debug("Raw data is incomplete. NeedMoreData event received")
                    break
                case CRC16CheckFailed():
                    logging.debug("Raw data is incorrect. CRCError event received")
                    self.transport.write(RejectPacket.code)
                    break
                case AVLPacket() | LoginPacket():
                    self.event_received(event)

    def event_received(self, event: AVLPacket | LoginPacket):
        """Prepare ASGI event and start processing."""
        asgi_event: dict[str, bytearray | str] = {"data": event.data}
        match event:
            case LoginPacket():
                asgi_event["type"] = "teltonika.login"
            case AVLPacket():
                asgi_event["type"] = "teltonika.avl"

        LOGGER.debug("Queuing event: {}".format(asgi_event))
        self.event_queue.put_nowait(asgi_event)

        asyncio.create_task(self.run_asgi())

    async def run_asgi(self):
        """Main ASGI entrypoint.

        This function emits event to the ASGI application.
        """
        scope = {
            "type": "teltonika",
            "client": self.transport.get_extra_info("peername"),
            "scheme": "tcp",
        }

        async def send(event):
            LOGGER.debug("Send event: {}".format(event))
            close = False
            match event["type"]:
                case "teltonika.login.accept":
                    msg = AcceptPacket.code
                case "teltonika.login.reject":
                    msg = RejectPacket.code
                    close = True
                case "teltonika.avl.accept":
                    msg = AckPacket(event["data"]).code
                case _:
                    close = True

            self.transport.write(msg)
            if close:
                self.transport.close()

        async def receive():
            return await self.event_queue.get()

        await self.app(scope, receive, send)
