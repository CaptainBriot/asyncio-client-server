"""TCP server that tracks the number of requests made every second.

Run:
python3.6 server.py
"""
import asyncio
import uuid
import logging

import common

LOGGER = logging.getLogger(__name__)


class TrackerServer:
    """A TCP server that keeps track of how many requests are made per second."""

    def __init__(self, host, port):
        """A TCP server that keeps track of how many requests are made per second.

        It uses a set() to keep track of how many requests were made. Items in the set are removed one second after
        creation using asyncio.call_later function.

        Args:
            host: the host address to listen on.
            port: the port to listen on.
        """
        self.host = host
        self.port = port
        self.requests = set()
        self.frequency = 1

    def start(self):
        """Start the server by scheduling coroutines with the asyncio event loop."""
        asyncio.ensure_future(asyncio.start_server(self.handle_request, self.host, self.port))
        asyncio.ensure_future(self.log_numbers_requests_per_second())

    async def handle_request(self, *_):
        """Handle incoming requests.

        Args:
            *_: (reader, writer) tuple not used in this case because we do not care about reading what the client sent
                and we do not need to write anything back to the client.
        """
        uid = uuid.uuid4()
        self.requests.add(uid)
        asyncio.get_event_loop().call_later(self.frequency, self.requests.remove, uid)

    async def log_numbers_requests_per_second(self, interval=0.5):
        """Log the current number of requests made per second.

        Args:
            interval: log the number of requests at interval seconds.
        """
        while True:
            LOGGER.info('%s requests/second', len(self.requests))
            await asyncio.sleep(interval)


def main():
    """Main entry point."""
    common.init_logging()
    server = TrackerServer('127.0.0.1', 8888)
    server.start()
    asyncio.get_event_loop().run_forever()
    asyncio.get_event_loop().close()


if __name__ == '__main__':
    main()
