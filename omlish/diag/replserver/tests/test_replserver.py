import contextlib
import os
import socket
import tempfile
import threading
import time

from .. import server as server_
from .... import lang
from ....testing import run_with_timeout


def test_replserver():
    def check(path):
        conn = socket.socket(socket.AF_UNIX)
        conn.settimeout(0.1)

        deadline = time.time() + 2
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
                with contextlib.suppress(socket.timeout):
                    buf += conn.recv(1024)
                if time.time() >= deadline:
                    raise ValueError
                if buf.endswith(b'>>> '):
                    break

            conn.send(b'1 + 2\n')

            buf = b''
            while True:
                with contextlib.suppress(socket.timeout):
                    buf += conn.recv(1024)
                if time.time() >= deadline:
                    raise ValueError
                if buf == b'3\n>>> ':
                    break

    def inner():
        server = server_.ReplServer(server_.ReplServer.Config(path))
        with lang.defer(lambda: server.shutdown(True, 2)):
            def run():
                with server:
                    server.run()

            thread = threading.Thread(target=run)
            thread.start()

            check(path)

            time.sleep(.1)

            server.shutdown()
            thread.join(3)
            assert not thread.is_alive()

    path = os.path.join(tempfile.mkdtemp(), 'sock')
    run_with_timeout(inner)
