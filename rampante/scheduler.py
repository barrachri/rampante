"""
Scheduler.

:copyright: (c) 2017, Christian Barra
:license: Apache2, see LICENSE for more details.
"""


import asyncio
import logging
from concurrent.futures import CancelledError

import msgpack

from .connector import streaming
from .decorator import _subscribers
from .worker import worker

log = logging.getLogger("rampante.scheduler")


async def scheduler(queue_size: int=10, loop: asyncio.AbstractEventLoop=None):
    """Launch the task manager."""
    if loop is None:
        loop = asyncio.get_event_loop()

    try:
        tasks_queue: asyncio.PriorityQueue = asyncio.PriorityQueue(maxsize=queue_size)
        worker_task = asyncio.ensure_future(worker(tasks_queue))

        async def on_message(msg):
            """Add tasks to the queue."""
            queue = msg.proto.subject
            log.info(f"Received a new event: {queue} - {msg.seq}")

            body = msgpack.unpackb(msg.data, encoding="utf-8")

            # Add tasks to the queue
            for func in _subscribers.get(queue, []):
                priority = body.get("priority", 1)
                entry = (priority, func, queue, body)
                log.info(f"Create a new task: `{func.__name__}` - priority {priority}")
                await tasks_queue.put(entry)

        log.info("Loading subscribers....")
        for queue_name, funcs in _subscribers.items():
            # add a callback when you receive a message
            await streaming.subscribe(queue_name, on_message)
            for func in funcs:
                log.info(f"Function `{func.__name__}` subscribed on `{queue_name}`")

        # really, really ugly
        while True:
            await asyncio.sleep(1)

    except CancelledError:
        log.warning("Closing tasks....")
        await tasks_queue.join()
        worker_task.cancel()
