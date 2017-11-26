import asyncio
import logging

import msgpack
from aiohttp import web
from aiokafka import AIOKafkaProducer

from rampante import scheduler, subscribe_on

log = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '[%(asctime)s %(name)s %(levelname)s] %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)
log.setLevel(logging.INFO)

KAFKA_URI = 'localhost:9092'


@subscribe_on("user.subscribed")
async def send_a_message(queue_name, data, producer):
    log.info("Event received!")


async def handle(request):
    name = request.match_info.get('name', "Anonymous")
    text = "Hello, " + name
    body = msgpack.packb({"message": "Hello", "priority": 3})
    await request.app['events_queue'].send_and_wait("user.subscribed", body)
    return web.Response(text=text)


async def start_event_connection(app):
    """Connect to Kafka."""
    connection = AIOKafkaProducer(loop=app.loop, bootstrap_servers=KAFKA_URI)
    await connection.start()
    app['events_queue'] = connection


async def stop_event_connection(app):
    """Close connection with Kafka."""
    if 'events_queue' in app:
        await app['events_queue'].stop()


async def start_task_manager(app):
    """Load task manager."""
    app['task_manager'] = asyncio.ensure_future(
        scheduler(kafka_uri=KAFKA_URI, loop=app.loop, queue_size=10))


async def stop_task_manager(app):
    """Cancel task manager."""
    if 'task_manager' in app:
        app['task_manager'].cancel()
        await app['task_manager']

if __name__ == '__main__':
    app = web.Application()
    app.router.add_get('/{name}', handle)
    # On-startup tasks
    app.on_startup.append(start_event_connection)
    app.on_startup.append(start_task_manager)
    # Clean-up tasks
    app.on_cleanup.append(stop_task_manager)
    app.on_cleanup.append(stop_event_connection)
    web.run_app(app)
