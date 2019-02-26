"""
Connector.

:copyright: (c) 2017, Christian Barra
:license: Apache2, see LICENSE for more details.
"""

import asyncio
import logging
from typing import (
    Awaitable,
    Callable,
    Dict,
    Optional,
    Union,
    List
)

import msgpack
import aioredis
from tenacity import retry, wait_random_exponential

log = logging.getLogger("rampante.connector")



loop = asyncio.get_event_loop()

async def go():
    redis = await aioredis.create_redis(
        'redis://localhost', loop=loop)
    await redis.set('my-key', 'value')
    val = await redis.get('my-key')
    print(val)
    redis.close()
    await redis.wait_closed()
loop.run_until_complete(go())


class _Streaming():
    """

    await streaming.start(server=queue_uri, client_name="service-spawner", loop=loop)

    """
    def __init__(self) -> None:
        self._redis = None
        self._status = False
        self._subscription: List = []
        self.service_group: Optional[str] = None

    @retry(wait=wait_random_exponential(multiplier=1, max=10))
    async def start(self, server: str, client_name: str, service_group: str, loop: asyncio.AbstractEventLoop=None):
        """Start connection with the streams."""
        if self._status is False:
            loop = loop or asyncio.get_event_loop()
            self.service_group = service_group
            self._redis = await aioredis.create_redis(server, loop=loop)
            self._status = True
            log.info("Streaming connected.")
        else:
            log.info("Streaming already connected.")

    async def publish(self, name: str, data: Dict) -> None:
        """Publish a message inside a queue."""
        if self._status:
            await self._redis.xadd(name, body)
            log.info(f"Event {data} published inside {name}")
        else:
            raise RuntimeError("Streaming is not active.")

    async def subscribe(self, name: str, callback: Union[Callable, Awaitable]):
        """Subscribe to a given channel."""
        self._subscription[name] = self._redis.xread([name], timeout=10)

    async def unsubscribe(self, name: str) -> None:
        """Unsubscribe from a given channel."""
        if name in self._subscription:
            await self._subscription[name].unsubscribe()

    async def stop(self) -> None:
        """Close all connections."""
        log.warning("Closing connections....")
        self._redis.close()
        await self._redis.wait_closed()
        self._status = False


streaming = _Streaming()
