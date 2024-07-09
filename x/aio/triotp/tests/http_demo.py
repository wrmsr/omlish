from triotp import supervisor
from myproject.asgi import app as asgi_app
from myproject.wsgi import app as wsgi_app

from hypercorn.middleware import TrioWSGIMiddleware
from hypercorn.config import Config
from hypercorn.trio import serve


async def start():
   config_a = Config()
   config_a.bind = ["localhost:8000"]

   config_b = Config()
   config_b.bind = ["localhost:8001"]

   children = [
     supervisor.child_spec(
       id='endpoint-a',
       task=serve,
       args=[asgi_app, config_a],
     ),
     supervisor.child_spec(
       id='endpoint-b',
       task=serve,
       args=[TrioWSGIMiddleware(wsgi_app), config_b],
     ),
   ]
   opts = supervisor.options()
   await supervisor.start(children, opts)
