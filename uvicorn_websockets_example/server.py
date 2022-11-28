from enum import Enum

import uvicorn

from uvicorn_websockets_example.asgi import ASGIApplication


class Subprotocol(str, Enum):
    ocpp16 = "ocpp1.6"
    ocpp20 = "ocpp2.0"
    ocpp201 = "ocpp2.0.1"


class MyASGIApplication(ASGIApplication):
    def select_subprotocol(self, subprotocols: list[str]) -> str:
        if Subprotocol.ocpp201 in subprotocols:
            return Subprotocol.ocpp201.value
        else:
            raise ValueError("No supported subprotocol available")


app = MyASGIApplication()

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=9000,
        log_level="debug",
        ws="websockets",
        # ws="wsproto",
    )
