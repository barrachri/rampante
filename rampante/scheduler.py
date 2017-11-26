"""
Scheduler.

:copyright: (c) 2017, Christian Barra
:license: Apache2, see LICENSE for more details.
"""


import asyncio
import logging
from concurrent.futures import CancelledError

import msgpack
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from .decorator import _subscribers
from .worker import worker

log = logging.getLogger("rampante.scheduler")


async def scheduler(kafka_uri: str, loop: asyncio.AbstractEventLoop=None, queue_size: int=10):
    """Launch the task manager."""
    if loop is None:
        loop = asyncio.get_event_loop()

    try:
        task_index = 0

        log.info("Loading subscribers....")
        for binding_key, funcs in _subscribers.items():
            for func in funcs:
                log.info(f"Function `{func.__name__}` subscribed on `{binding_key}`")

        # Connect to Kafka
        consumer = AIOKafkaConsumer(
            *_subscribers.keys(), loop=loop, bootstrap_servers=kafka_uri)
        producer = AIOKafkaProducer(loop=loop, bootstrap_servers=kafka_uri)
        await producer.start()

        tasks_queue: asyncio.PriorityQueue = asyncio.PriorityQueue(maxsize=queue_size)
        worker_task = asyncio.ensure_future(worker(tasks_queue, producer))

        # Start listening on the queues/topics
        await consumer.start()
        log.info(f"Kafka consumer started.")

        async for message in consumer:

            log.info(f"Received a new event: {message.topic}")
            # selecter will yield functions to run
            for func in _subscribers.get(message.topic, []):
                body = msgpack.unpackb(message.value, encoding='utf-8')
                priority = body.get("priority", 1)
                entry = (priority, task_index, func, message.topic, body)
                log.info(f"Create a new task: `{func.__name__}` - priority {priority} - index {task_index}")
                await tasks_queue.put(entry)
                task_index += 1

    except CancelledError:
        log.warning("Closing background task manager.....")
        await consumer.stop()
        await producer.stop()
        log.warning("Kafka connector stopped.")
        log.warning("Closing tasks....")
        worker_task.cancel()
        await tasks_queue.join()
