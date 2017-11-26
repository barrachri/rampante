"""
Rampante Library
~~~~~~~~~~~~~~~~~~~~~
Requests is an HTTP library, written in Python, for human beings. Basic GET
usage:
   >>> import rampante
   >>> r = requests.get('https://www.python.org')
   >>> r.status_code
   200
   >>> 'Python is a programming language' in r.content
   True
... or POST:
   >>> payload = dict(key1='value1', key2='value2')
   >>> r = requests.post('http://httpbin.org/post', data=payload)
   >>> print(r.text)
   {
     ...
     "form": {
       "key2": "value2",
       "key1": "value1"
     },
     ...
   }
The other HTTP methods are supported - see `requests.api`. Full documentation
is at <http://python-requests.org>.
:copyright: (c) 2017 by Kenneth Reitz.
:license: Apache 2.0, see LICENSE for more details.
"""

from .decorator import subscribe_on
from .scheduler import scheduler


__all__ = ("subscribe_on", "scheduler")
