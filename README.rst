.. image:: https://badge.fury.io/py/rampante.svg
   :target: https://badge.fury.io/py/rampante
   :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/rampante.svg
   :target: https://pypi.org/project/rampante/
   :alt: Python Versions

.. image:: https://travis-ci.org/barrachri/rampante.svg?branch=master
    :target: https://travis-ci.org/barrachri/rampante

.. image:: https://codecov.io/gh/barrachri/rampante/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/barrachri/rampante

🐎 Rampante
================================================
A fancy and opinionated nanoframework for microservices.

Installation
===============

.. code-block:: sh

   pip install rampante

How to use `subscribe_on`
============================

.. code-block:: python

    from rampante import subscribe_on

    # The function should accept 3 params
    # queue_name, for example could be "user.subscribed"
    # data is a dictionary, it's a msgpacked message sent to Kafka
    # producer is an instance of AIOKafkaProducer, if you want to send new events

    @subscribe_on("user.subscribed")
    async def send_a_message(queue_name, data, producer):
        log.info("Event received!")

    @subscribe_on("user.subscribed", "user.created")
    async def send_another_message(queue_name, data, producer):
        log.info("Event received!")


Example
========================

.. code-block:: python

    import asyncio
    import logging

    import msgpack
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


Example with aiohttp
========================

.. code-block:: python

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

The name
================================================

Rampante means "rampant" in Italian.

Why Kafka?
================================================

I like aiokafka, but I plan to switch to Redis as soon as `Stream` will be officially available.

To Do
================================================

- add circuit breaker
- add retry
- add logic when tasks fail
- add consumer position

Pull requests are encouraged!

License
================================================

Apache 2.0
