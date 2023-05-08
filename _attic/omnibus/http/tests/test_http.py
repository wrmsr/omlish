import contextlib
import threading
import time
import typing as ta

import requests

from .. import apps as apps_
from .. import bind as bind_
from .. import consts as consts_
from .. import wsgiref as wsgiref_
from ... import json
from ...dev.testing import run_with_timeout


def test_inline_http():
    server: ta.Optional[wsgiref_.WsgiServer] = None

    def app(environ, start_response):
        assert environ['PATH_INFO'] == '/test'
        start_response(consts_.STATUS_OK, [])
        server.shutdown()
        return [b'hi']

    port = 9999

    def fn1():
        time.sleep(0.5)
        while True:
            try:
                response: requests.Response
                with contextlib.closing(requests.post(f'http://localhost:{port}/test', timeout=0.1)) as response:
                    if response.status_code == 200:
                        return
            except requests.RequestException:
                pass
            time.sleep(0.1)

    thread = threading.Thread(target=fn1)
    thread.start()

    with wsgiref_.ThreadSpawningWsgiRefServer(bind_.TcpBinder(bind_.TcpBinder.Config('0.0.0.0', port)), app) as server:
        with server.loop_context() as loop:
            port = server.binder.port
            for _ in loop:
                pass

    thread.join()


def test_http():
    # FIXME: dynamic port
    server: ta.Optional[wsgiref_.WsgiServer] = None

    def app(environ, start_response):
        assert environ['PATH_INFO'] == '/test'
        start_response(consts_.STATUS_OK, [])
        server.shutdown()
        return [b'hi']

    port = 8181

    def fn0():
        nonlocal server
        server = wsgiref_.ThreadSpawningWsgiRefServer(bind_.TcpBinder(bind_.TcpBinder.Config('0.0.0.0', port)), app)
        server.run()

    def fn1():
        time.sleep(0.5)
        while True:
            try:
                response: requests.Response
                with contextlib.closing(requests.post(f'http://localhost:{port}/test', timeout=0.1)) as response:
                    if response.status_code == 200:
                        return
            except requests.RequestException:
                pass
            time.sleep(0.1)

    run_with_timeout(fn0, fn1)


def test_json_http():
    server: ta.Optional[wsgiref_.WsgiServer] = None

    def json_app(obj):
        server.shutdown()
        return {'hi': True}

    port = 9998

    def fn1():
        time.sleep(0.5)
        while True:
            try:
                response: requests.Response
                with contextlib.closing(requests.post(f'http://localhost:{port}/test', timeout=0.1)) as response:
                    if response.status_code == 200:
                        assert json.loads(response.content) == {'hi': True}
                        return
            except requests.RequestException:
                pass
            time.sleep(0.1)

    thread = threading.Thread(target=fn1)
    thread.start()

    with wsgiref_.ThreadSpawningWsgiRefServer(bind_.TcpBinder(bind_.TcpBinder.Config('0.0.0.0', 0)), apps_.simple_json_app(json_app)) as server:  # noqa as server:
        with server.loop_context() as loop:
            port = server.binder.port
            for _ in loop:
                pass

    thread.join()
