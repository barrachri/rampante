import asyncio
import os

import msgpack
import pytest
from aiokafka import AIOKafkaProducer

from rampante import scheduler, subscribe_on


@pytest.mark.asyncio
async def test_scheduler():
    KAFKA_URI = os.getenv("KAFKA_URI", "localhost:9092")
    check = None

    loop = asyncio.get_event_loop()

    @subscribe_on("create.something")
    async def add_2_numbers(topic, data, sender):
        nonlocal check
        check = data['message']
        await asyncio.sleep(2)
        return check

    worker_task = asyncio.ensure_future(scheduler(kafka_uri=KAFKA_URI, queue_size=10))
    kafka_producer = AIOKafkaProducer(loop=loop, bootstrap_servers=KAFKA_URI)
    await kafka_producer.start()

    await asyncio.sleep(2)

    body = msgpack.packb({"message": "Hello"})
    await kafka_producer.send_and_wait("create.something", body)
    await asyncio.sleep(2)
    await kafka_producer.stop()
    worker_task.cancel()
    await asyncio.sleep(2)

    assert check == "Hello"
