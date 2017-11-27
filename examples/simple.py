import asyncio
import logging

from rampante import scheduler, streaming, subscribe_on

log = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '[%(asctime)s %(name)s %(levelname)s] %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)
log.setLevel(logging.INFO)

STREAM_URI = "nats://127.0.0.1:4222"


@subscribe_on("user.subscribed")
async def send_a_message(queue_name, data):
    check = data['message']
    log.info(check)


async def main(loop):
    """Start queue manager."""
    await streaming.start(server=STREAM_URI, client_name="service-01", service_group="service-spawner", loop=loop)


async def clean(loop):
    """Stop queue manager."""
    await streaming.stop()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main(loop))
        loop.run_until_complete(scheduler(queue_size=10))
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(clean(loop))
        log.warning("Shutting down!")
