import asyncio

import websockets
import logging

logging.basicConfig(
    format="%(message)s",
    level=logging.DEBUG,
)


async def main():
    """Helper function to establish connection to Central System."""
    async with websockets.connect(
        "ws://localhost:9000",
        subprotocols=["ocpp2.0.1"],
    ):
        print("Connection ok")


if __name__ == "__main__":
    asyncio.run(main())
