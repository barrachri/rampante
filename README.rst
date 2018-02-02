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
    # data is a dictionary, it's a msgpacked message sent to NATS
    # app, aiohttp app instance (in case)

    @subscribe_on("user.subscribed")
    async def send_a_message(queue_name, data, app):
        log.info("Event received!")

    @subscribe_on("user.subscribed", "user.created")
    async def send_another_message(queue_name, data, app):
        log.info("Event received!")


Example
========================

Check the examples inside the folder!

You need a nats-streaming:0.6.0 running, check the Makefile :)


The name
================================================

Rampante means "rampant" in Italian.

Why NATS?
================================================

It's written in Go and seems working really well!

To Do
================================================

- add retry/logic when tasks fail

Pull requests are encouraged!

License
================================================

Apache 2.0
