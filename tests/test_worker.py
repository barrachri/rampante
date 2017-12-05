import asyncio

import pytest

from rampante.worker import worker


@pytest.mark.asyncio
async def test_worker():
    queue = asyncio.PriorityQueue(maxsize=10)
    check = None

    async def add_2_numbers(topic, data, app):
        nonlocal check
        check = "TaskDone"
        await asyncio.sleep(2)
        return check

    worker_task = asyncio.ensure_future(worker(queue))

    entry = (1, add_2_numbers, 'my.event', {})
    await queue.put(entry)
    await queue.join()

    worker_task.cancel()

    assert check == "TaskDone"
