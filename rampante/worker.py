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


async def worker(queue: asyncio.PriorityQueue):
    """Executor of tasks.

    :args queue: an asyncio.PriorityQueue.
    """
    log.info("Worker loaded...")
    try:
        while True:
            now = time.time()
            task = await queue.get()
            func = task[1]
            func_name = func.__name__
            log.info(f"Executing task `{func_name}` subscribed on `{task[2]}`")
            try:
                await func(task[2], task[3])
            except CancelledError:
                log.warning(f"Task `{func_name}` cancelled.")
                raise
            except Exception as err:
                log.exception(f"Task `{func_name}` failed.")
            else:
                executione_time = time.time() - now
                log.info(f"Task `{func_name}` completed in {executione_time:.5f} secs.")
            finally:
                queue.task_done()
                log.info(f"Task `{func_name}` removed from the queue.")
    except CancelledError:
        log.warning("Consumer cancelled.")
