import asyncio
import logging

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


async def stop_task_manager(app):
    """Cancel task manager."""
    if 'task_manager' in app:
        app['task_manager'].cancel()
        await app['task_manager']

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(scheduler(kafka_uri=KAFKA_URI, loop=loop, queue_size=10))
    except KeyboardInterrupt:
        log.warning("Shutting down!")
