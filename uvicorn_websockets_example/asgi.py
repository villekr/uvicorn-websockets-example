from enum import Enum
from typing import Any, Awaitable, Callable, MutableMapping

from loguru import logger as log


class ASGIScope(str, Enum):
    lifespan = "lifespan"
    websocket = "websocket"
    http = "http"


class ASGILifeSpanEvent(str, Enum):
    startup = "lifespan.startup"
    shutdown = "lifespan.shutdown"


class ASGIWebSocketEvent(str, Enum):
    # receive
    connect = "websocket.connect"
    receive = "websocket.receive"
    disconnect = "websocket.disconnect"
    # send
    accept = "websocket.accept"
    send = "websocket.send"
    close = "websocket.close"


class ASGIHTTPEvent(str, Enum):
    disconnect = "http.disconnect"
    request = "http.request"
    response_start = "http.response.start"
    response_body = "http.response.body"


class ASGILifeSpanStartup(str, Enum):
    complete = "lifespan.startup.complete"
    failed = "lifespan.startup.failed"


class ASGILifeSpanShutDown(str, Enum):
    complete = "lifespan.shutdown.complete"
    failed = "lifespan.shutdown.failed"


Scope = MutableMapping[str, Any]
Message = MutableMapping[str, Any]

Receive = Callable[[], Awaitable[Message]]
Send = Callable[[Message], Awaitable[None]]

ASGIAppSignature = Callable[[Scope, Receive, Send], Awaitable[None]]


class ASGIApplication:
    """ASGI Application to handle event based message routing."""

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        """ASGI signature handler.

        Args:
            scope (Scope): ASGI scope
            receive (Receive): ASGI handle for receiving messages
            send (Send): ASGI handle for sending messages
        """

        if scope["type"] in [ASGIScope.websocket, ASGIScope.http]:
            await self.handler(scope, receive, send)
        elif scope["type"] == ASGIScope.lifespan:
            await self.lifespan_handler(scope, receive, send)
        else:
            raise ValueError(f'Unsupported ASGI scope type: {scope["type"]}')

    async def lifespan_handler(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:
        event = await receive()
        if event["type"] == ASGILifeSpanEvent.startup.value:
            try:
                await send({"type": ASGILifeSpanStartup.complete.value})
            except Exception as e:
                log.error(f"Exception on startup {e}")
                await send({"type", ASGILifeSpanStartup.failed.value})
        elif event["type"] == ASGILifeSpanEvent.shutdown.value:
            try:
                await send({"type": ASGILifeSpanShutDown.complete.value})
            except Exception as e:
                log.error(f"Exception on shutdown {e}")
                await send({"type", ASGILifeSpanShutDown.failed.value})

    async def handler(self, scope: Scope, receive: Receive, send: Send):
        log.debug(f"{scope=}")
        while True:
            event = await receive()
            log.debug(f"{event=}")

            # WebSocket
            if event["type"] == ASGIWebSocketEvent.receive:
                log.debug(event["body"])
            elif event["type"] == ASGIWebSocketEvent.connect:
                subprotocol: str = self.select_subprotocol(scope["subprotocols"])
                await send({"type": "websocket.accept", "subprotocol": subprotocol})
            elif event["type"] == ASGIWebSocketEvent.disconnect:
                break

            # HTTP
            elif event["type"] == ASGIHTTPEvent.request:
                raise ValueError("Not supported")
            elif event["type"] == ASGIHTTPEvent.disconnect.value:
                break

    # Override in subclass
    def select_subprotocol(self, subprotocols: list[str]) -> str:
        raise NotImplementedError
