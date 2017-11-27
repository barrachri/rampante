"""
Connector.

:copyright: (c) 2017, Christian Barra
:license: Apache2, see LICENSE for more details.
"""

import asyncio
import logging
from typing import Awaitable, Callable, Dict, Union

import msgpack
from nats.aio.client import Client as NATS
from stan.aio.client import Client as STAN

log = logging.getLogger("rampante.connector")


class _Streaming():
    """

    await streaming.start(server=queue_uri, client_name="service-spawner", loop=loop)

    """
    def __init__(self) -> None:
        self._nc: NATS = None
        self._sc: STAN = None
        self._status = False
        self._subscription: Dict = {}
        self.service_group: str = None

    async def start(self, server: str, client_name: str, service_group: str, loop: asyncio.AbstractEventLoop=None):
        """Start connection with the stream


        """
        if self._status is False:
            loop = loop or asyncio.get_event_loop()
            self.service_group = service_group
            self._nc = NATS()
            await self._nc.connect(servers=[server], io_loop=loop)
            # Start session with NATS Streaming cluster.
            self._sc = STAN()
            await self._sc.connect("test-cluster", client_name, nats=self._nc)
            self._status = True
            log.info("Streaming connected.")
        else:
            log.info("Streaming already connected.")

    async def publish(self, name: str, data: Dict):
        """Unsubscribe from to a given channel."""
        if self._status:
            body = msgpack.packb(data)
            await self._sc.publish(name, body)
        else:
            raise RuntimeError("Streaming is not active.")

    async def subscribe(self, name: str, callback: Union[Callable, Awaitable]):
        """Unsubscribe from to a given channel."""
        self._subscription[name] = await self._sc.subscribe(name, queue=self.service_group, durable_name="durable", cb=callback)

    async def unsubscribe(self, name):
        """Unsubscribe from a given channel."""
        if name in self._subscription:
            await self._subscription[name].unsubscribe()

    async def stop(self):
        """Close all connections."""
        log.warning("Closing connections....")
        for subsciption in self._subscription.values():
            await subsciption.unsubscribe()
        await self._sc.close()
        await self._nc.close()
        self._status = False
        self.publish = None


streaming = _Streaming()
