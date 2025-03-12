"""
FIXME:
 - lol shutdown deadlocks
 - whole thing is just gross is this its own thread or what
 - cli with client helper too

TODO:
 - !!! ANYIO !!!
 - optional paramiko ssh-server
 - optional ipython embed
 - https://github.com/python/cpython/tree/56470004e58911b146c016fc9fec4461b8f69454/Lib/_pyrepl

See:
 - https://github.com/vxgmichel/aioconsole/blob/e55f4b0601da3b3a40a88c965526d35ab38b5841/aioconsole/server.py
 - https://github.com/nhoad/aiomanhole
 - https://github.com/twisted/twisted/blob/00aa56f5257060304d41f09651c6ab58ee6104d6/src/twisted/conch/manhole.py
  - https://github.com/Yelp/Tron/blob/4b864a73bd129b03e9890c134212972452bc6ab0/tron/manhole.py#L8
 - https://github.com/ionelmc/python-manhole
 - https://github.com/python/cpython/tree/15d48aea02099ffc5bdc5511cc53ced460cb31b9/Lib/_pyrepl

socat - UNIX-CONNECT:repl.sock
"""
import contextlib
import functools
import logging
import os
import socket as sock
import threading
import typing as ta
import weakref

from ... import check
from ... import dataclasses as dc
from .console import InteractiveSocketConsole


log = logging.getLogger(__name__)


class ReplServer:
    CONNECTION_THREAD_NAME = 'ReplServerConnection'

    @dc.dataclass(frozen=True)
    class Config:
        path: str
        file_mode: int | None = 0o660
        poll_interval: float = 0.5
        exit_timeout: float = 10.0

    def __init__(
            self,
            config: Config,
    ) -> None:
        super().__init__()

        check.not_empty(config.path)
        self._config = check.isinstance(config, ReplServer.Config)

        self._socket: sock.socket | None = None
        self._is_running = False
        self._consoles_by_threads: ta.MutableMapping[threading.Thread, InteractiveSocketConsole] = \
            weakref.WeakKeyDictionary()  # noqa
        self._is_shutdown = threading.Event()
        self._should_shutdown = False

    @property
    def path(self) -> str:
        return self._config.path

    def __enter__(self) -> ta.Self:
        check.state(not self._is_running)
        check.state(not self._is_shutdown.is_set())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if not self._is_shutdown.is_set():
            self.shutdown(True, self._config.exit_timeout)

    def run(self) -> None:
        check.state(not self._is_running)
        check.state(not self._is_shutdown.is_set())

        if os.path.exists(self._config.path):
            os.unlink(self._config.path)

        self._socket = sock.socket(sock.AF_UNIX, sock.SOCK_STREAM)
        self._socket.settimeout(self._config.poll_interval)

        if self._config.file_mode is not None:
            prev_umask = os.umask(~self._config.file_mode)
        else:
            prev_umask = None
        try:
            self._socket.bind(self._config.path)
        finally:
            if prev_umask is not None:
                os.umask(prev_umask)

        with contextlib.closing(self._socket):
            self._socket.listen(1)

            log.info('Repl server listening on file %s', self._config.path)

            self._is_running = True
            try:
                while not self._should_shutdown:
                    try:
                        conn, _ = self._socket.accept()
                    except TimeoutError:
                        continue

                    log.info('Got repl server connection on file %s', self._config.path)

                    def run(conn):
                        with contextlib.closing(conn):
                            variables = globals().copy()

                            console = InteractiveSocketConsole(conn, variables)
                            variables['__console__'] = console

                            log.info(
                                'Starting console %x repl server connection on file %s on thread %r',
                                id(console),
                                self._config.path,
                                threading.current_thread().ident,
                            )
                            self._consoles_by_threads[threading.current_thread()] = console
                            console.interact()

                    thread = threading.Thread(
                        target=functools.partial(run, conn),
                        daemon=True,
                        name=self.CONNECTION_THREAD_NAME)
                    thread.start()

                for console in self._consoles_by_threads.values():
                    try:
                        console.conn.close()
                    except Exception:
                        log.exception('Error shutting down')

                for thread in self._consoles_by_threads:
                    try:
                        thread.join(self._config.exit_timeout)
                    except Exception:
                        log.exception('Error shutting down')

                os.unlink(self._config.path)

            finally:
                self._is_shutdown.set()
                self._is_running = False

    def shutdown(self, block: bool = False, timeout: float | None = None) -> None:
        self._should_shutdown = True
        if block:
            self._is_shutdown.wait(timeout=timeout)


def run() -> None:
    with ReplServer(ReplServer.Config('repl.sock')) as repl_server:
        repl_server.run()
