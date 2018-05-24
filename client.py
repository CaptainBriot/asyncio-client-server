"""Throttling TCP client script (see 'ThrottlingClient' class for mote information)

Send up to 1 requests per second:
python3.6 client.py 1

Send up to 10 requests per second:
python3.6 client.py 20

Send up to 100 requests per second:
python3.6 client.py 100

Send up to N requests per second:
python3.6 client.py N
"""
import asyncio
import logging
import argparse
import itertools
import time

import common

LOGGER = logging.getLogger(__name__)


class BasicRateLimitingProtocol:
    """A basic rate limiting protocol.

    Note: see 'start' function for more information about the send rate.
              This class will ensure that the maximum number of requests per second tends to 'frequency' and in practice
              will be lower than this limit.
    """
    def __init__(self, callback, period):
        """A basic rate limiting protocol.

        Args:
            callback: function to call when at given frequency.
            period: how many call to callback should be made per second?
        """
        self.callback = callback
        self.frequency = 1 / period

    async def start(self):
        """Make (schedule) requests.

        Note: This is not as accurate as expected. One reason is because of the overhead when creating the coroutine.
              when period is 10 the change is not significant enough to see.
              when the period is 100 the average send is 90
              when the period is 200 the average send is 166
        """
        while True:
            asyncio.ensure_future(self.callback())  # ensure_future is faster than await in this case.
            await asyncio.sleep(self.frequency)


class TokenBucketRateLimitingProtocol(BasicRateLimitingProtocol):
    """A token bucket rate limiting protocol.

    The protocol has a number of tokens it can give away and at a scheduled interval the bucket tokens get's
    replenished by a given amount. When no token is available then the callback does not get called.
    """
    def __init__(self, callback, period):
        """A token bucket rate limiting protocol.

        Args:
            callback: function to call when at given frequency.
            period: how many call to callback should be made per second?
        """
        super().__init__(callback, period)
        self.period = period

        if self.period < 1:
            self.max_tokens = 1
        else:
            self.max_tokens = self.period

        self.tokens = 0  # The bucket starts empty to avoid having a burst of requests when the protocol starts.
        self.updated_at = time.monotonic()

    async def wait(self):
        """Async wait until a token is available in the bucket."""
        while self.tokens < 1:
            self.add_new_tokens()
            await asyncio.sleep(self.frequency)
        self.tokens -= 1

    def add_new_tokens(self):
        """Add new tokens to the bucket depending on how much time has elapsed since the last update."""
        now = time.monotonic()
        time_since_update = now - self.updated_at
        new_tokens = time_since_update * self.period

        if new_tokens >= 1:
            self.tokens = min(self.tokens + new_tokens, self.max_tokens)
            self.updated_at = now

    async def start(self):
        """Make requests for each available token in the bucket."""
        while True:
            await self.wait()
            asyncio.ensure_future(self.callback())


class ThrottlingClient:
    """A TCP client that throttle requests"""

    def __init__(self, host, port, period, protocol=TokenBucketRateLimitingProtocol):
        """A TCP client that throttle requests.

        Args:
            host: the host address to connect to.
            port: the port to connect to.
            period: how many requests should be sent per second?
        """
        self.host = host
        self.port = port
        self.counter = itertools.count()
        self.protocol = protocol(self.send, period)
        self.start = self.protocol.start

    async def send(self):
        """Send one request."""
        try:
            _, writer = await asyncio.open_connection(self.host, self.port)
        except ConnectionError as ex:
            LOGGER.error(ex)
            return

        counter = str(next(self.counter))
        LOGGER.info('%s: sending request to server', counter)
        writer.write(counter.encode())
        writer.close()


def parse_args():  # pragma: no cover
    """Parse command lin arguments.

    Returns:
        the command line options.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('period', type=float, help="the rate as defined in 'frequency = 1 / period'")
    return parser.parse_args()


def main():
    """Main entry point."""
    common.init_logging()
    options = parse_args()
    client = ThrottlingClient('127.0.0.1', 8888, options.period)
    asyncio.get_event_loop().run_until_complete(client.start())
    asyncio.get_event_loop().close()


if __name__ == '__main__':
    main()
