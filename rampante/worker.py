"""
Worker.

:copyright: (c) 2017, Christian Barra
:license: Apache2, see LICENSE for more details.
"""


import asyncio
import logging
import time
from concurrent.futures import CancelledError

log = logging.getLogger("rampante.worker")


async def worker(queue: asyncio.PriorityQueue, producer):
    """Executor of tasks.

    :args queue: an asyncio.PriorityQueue queue.
    :args producer: an instance of a KafkaProducer in case your tasks need to fire new events.
    """
    try:
        while True:
            now = time.time()

            # wait for an item from the producer
            task = await queue.get()
            func = task[2]
            log.info(f"Executing task `{task[2].__name__}` subscribed on `{task[3]}`")
            try:
                await func(task[3], task[4], producer)
            except CancelledError:
                log.warning(f"Task `{task[2].__name__}` cancelled.")
                raise
            except Exception as err:
                log.exception(f"Task `{task[2].__name__}` failed.")
            else:
                executione_time = time.time() - now
                log.info(f"Task `{task[2].__name__}` completed in {executione_time:.5f} secs.")
            finally:
                queue.task_done()
                log.info(f"Task `{task[2].__name__}` removed.")
    except CancelledError:
        log.warning("Consumer cancelled.")
