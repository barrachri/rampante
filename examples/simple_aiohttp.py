import asyncio
import logging

from aiohttp import web

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
    log.info("Event received!")


async def handle(request):
    name = request.match_info.get('name', "Anonymous")
    text = "Hello, " + name
    body = {"message": "Hello", "priority": 3}
    await streaming.publish("user.subscribed", body)
    return web.Response(text=text)


async def start_task_manager(app):
    """Connect to Kafka."""
    await streaming.start(server=STREAM_URI, client_name="service-01", service_group="service-spawner", loop=app.loop)
    app['task_manager'] = asyncio.ensure_future(
        scheduler(loop=app.loop, queue_size=10))


async def stop_task_manager(app):
    """Cancel task manager."""
    await streaming.stop()
    if 'task_manager' in app:
        app['task_manager'].cancel()
        await app['task_manager']

if __name__ == '__main__':
    app = web.Application()
    app.router.add_get('/{name}', handle)
    # On-startup tasks
    app.on_startup.append(start_task_manager)
    # Clean-up tasks
    app.on_cleanup.append(stop_task_manager)
    web.run_app(app)
