import contextlib
import os
import socket
import tempfile
import threading
import time

from .. import server as server_
from ... import lang
from ...dev.testing import run_with_timeout


def test_replserver():
    def check(path):
        conn = socket.socket(socket.AF_UNIX)
        conn.settimeout(0.1)

        deadline = time.time() + 3
        while True:
            try:
                conn.connect(path)
            except OSError:
                pass
            else:
                break
            if time.time() >= deadline:
                raise ValueError

        with contextlib.closing(conn):
            buf = b''
            while True:
                try:
                    buf += conn.recv(1024)
                except socket.timeout:
                    pass
                if time.time() >= deadline:
                    raise ValueError
                if buf.endswith(b'>>> '):
                    break

            conn.send(b'1 + 2\n')

            buf = b''
            while True:
                try:
                    buf += conn.recv(1024)
                except socket.timeout:
                    pass
                if time.time() >= deadline:
                    raise ValueError
                if buf == b'3\n>>> ':
                    break

    def inner():
        server = server_.ReplServer(server_.ReplServer.Config(path))
        with lang.defer(lambda: server.shutdown(True, 5)):
            def run():
                with server:
                    server.run()

            thread = threading.Thread(target=run)
            thread.start()

            check(path)

            time.sleep(1)

            server.shutdown()
            thread.join(3)

    path = os.path.join(tempfile.mkdtemp(), 'sock')
    run_with_timeout(inner)
