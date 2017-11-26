"""
Decorator to add subscribers.

:copyright: (c) 2017, Christian Barra
All rights reserved.
"""


import logging
from typing import Dict

log = logging.getLogger("rampante.decorator")


_subscribers: Dict = {}


def subscribe_on(*routing_keys: str):
    """Add the decorated function as a callback for the given routing key/s.

    @listen_on("user.registered")
    async def my_task():
        # do something
        pass

    @listen_on("user.registered", "user.reset-password")
    async def my_task():
        # do something
        pass

    :args routing_keys: list of routing keys.
    """
    def decorator(func):
        for routing_key in routing_keys:
            if routing_key in _subscribers:
                _subscribers[routing_key] = _subscribers[routing_key] + (func,)
            else:
                _subscribers[routing_key] = (func,)
        return func

    return decorator
