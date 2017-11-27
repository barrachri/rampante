"""
Rampante Library.
~~~~~~~~~~~~~~~~~~~~~

A fancy and opinionated nanoframework for microservices.

:copyright: (c) 2017 by Christian barra.
:license: Apache 2.0, see LICENSE for more details.
"""

from .decorator import subscribe_on
from .scheduler import scheduler
from .connector import streaming
from .__version__ import __version__


__all__ = ("subscribe_on", "scheduler", "streaming")
