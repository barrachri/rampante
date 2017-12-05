import asyncio
import os

import pytest

from rampante import scheduler, streaming, subscribe_on


@pytest.mark.asyncio
async def test_scheduler():
    STREAM_URI = os.getenv("STREAM_URI", "nats://127.0.0.1:4222")
    check = None

    loop = asyncio.get_event_loop()

    @subscribe_on("user.subscribed")
    async def add_2_numbers(topic, data, app):
        nonlocal check
        check = data['message']
        await asyncio.sleep(1)
        return check

    await streaming.start(server=STREAM_URI, client_name="service-01", service_group="service-spawner", loop=loop)
    worker_task = asyncio.ensure_future(scheduler(queue_size=10))
    await asyncio.sleep(1)
    await streaming.publish("user.subscribed", {"message": "Hello"})
    await asyncio.sleep(1)
    worker_task.cancel()
    await streaming.stop()
    assert check == "Hello"
