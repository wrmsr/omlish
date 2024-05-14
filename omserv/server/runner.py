"""
BSD 2-Clause License

Copyright (c) 2019-2023, Almar Klein, Korijn van Golen
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import collections.abc
import asyncio
import functools
import socket
import contextlib
import os
import logging
import typing as ta
import weakref

import aiohttp.web as aweb
from omlish import dataclasses as dc


try:
    from ssl import SSLContext
except ImportError:
    SSLContext = object  # type: ignore[misc,assignment]


class suppress(contextlib.AbstractContextManager):
    """
    Context manager to suppress specified exceptions

    After the exception is suppressed, execution proceeds with the next
    statement following the with statement.

         with suppress(FileNotFoundError):
             os.remove(somefile)
         # Execution still resumes here if the file was already removed
    """

    def __init__(self, *exceptions):
        super().__init__()
        self._exceptions = exceptions

    def __enter__(self):
        pass

    def __exit__(self, exctype, excinst, exctb):
        # Unlike isinstance and issubclass, CPython exception handling currently only looks at the concrete type
        # hierarchy (ignoring the instance and subclass checking hooks). While Guido considers that a bug rather than a
        # feature, it's a fairly hard one to fix due to various internal implementation details. suppress provides the
        # simpler issubclass based semantics, rather than trying to exactly reproduce the limitations of the CPython
        # interpreter.
        #
        # See http://bugs.python.org/issue12029 for more details
        return exctype is not None and issubclass(exctype, self._exceptions)


def _cancel_tasks(
        to_cancel: set["asyncio.Task[ta.Any]"],
        loop: asyncio.AbstractEventLoop,
) -> None:
    if not to_cancel:
        return

    for task in to_cancel:
        task.cancel()

    loop.run_until_complete(asyncio.gather(*to_cancel, return_exceptions=True))

    for task in to_cancel:
        if task.cancelled():
            continue
        if task.exception() is not None:
            loop.call_exception_handler({
                "message": "unhandled exception during asyncio.run() shutdown",
                "exception": task.exception(),
                "task": task,
            })


@dc.dataclass(frozen=True)
class SitesConfig:
    host: ta.Optional[ta.Union[str, aweb.HostSequence]] = None
    port: ta.Optional[int] = None
    path: ta.Union[os.PathLike, ta.Iterable[os.PathLike], None] = None
    sock: ta.Optional[ta.Union[socket.socket, ta.Iterable[socket.socket]]] = None
    ssl_context: ta.Optional[SSLContext] = None
    backlog: int = 128
    reuse_address: ta.Optional[bool] = None
    reuse_port: ta.Optional[bool] = None


def make_sites(runner: aweb.AppRunner, cfg: SitesConfig) -> list[aweb.BaseSite]:
    sites: list[aweb.BaseSite] = []

    if cfg.host is not None:
        if isinstance(cfg.host, (str, bytes, bytearray, memoryview)):
            sites.append(
                aweb.TCPSite(
                    runner,
                    cfg.host,
                    cfg.port,
                    ssl_context=cfg.ssl_context,
                    backlog=cfg.backlog,
                    reuse_address=cfg.reuse_address,
                    reuse_port=cfg.reuse_port,
                )
            )
        else:
            for h in cfg.host:
                sites.append(
                    aweb.TCPSite(
                        runner,
                        h,
                        cfg.port,
                        ssl_context=cfg.ssl_context,
                        backlog=cfg.backlog,
                        reuse_address=cfg.reuse_address,
                        reuse_port=cfg.reuse_port,
                    )
                )
    elif cfg.path is None and cfg.sock is None or cfg.port is not None:
        sites.append(
            aweb.TCPSite(
                runner,
                port=cfg.port,
                ssl_context=cfg.ssl_context,
                backlog=cfg.backlog,
                reuse_address=cfg.reuse_address,
                reuse_port=cfg.reuse_port,
            )
        )

    if cfg.path is not None:
        if isinstance(cfg.path, (str, os.PathLike)):
            sites.append(
                aweb.UnixSite(
                    runner,
                    cfg.path,
                    ssl_context=cfg.ssl_context,
                    backlog=cfg.backlog,
                )
            )
        else:
            for p in cfg.path:
                sites.append(
                    aweb.UnixSite(
                        runner,
                        p,
                        ssl_context=cfg.ssl_context,
                        backlog=cfg.backlog,
                    )
                )

    if cfg.sock is not None:
        if not isinstance(cfg.sock, collections.abc.Iterable):
            sites.append(
                aweb.SockSite(
                    runner,
                    cfg.sock,
                    ssl_context=cfg.ssl_context,
                    backlog=cfg.backlog,
                )
            )
        else:
            for s in cfg.sock:
                sites.append(
                    aweb.SockSite(
                        runner,
                        s,
                        ssl_context=cfg.ssl_context,
                        backlog=cfg.backlog,
                    )
                )

    return sites


async def _run_app(
        app: ta.Union[aweb.Application, ta.Awaitable[aweb.Application]],
        *,
        sites_cfg: SitesConfig = SitesConfig(),

        shutdown_timeout: float = 60.0,
        keepalive_timeout: float = 75.0,
        print: ta.Optional[ta.Callable[..., None]] = print,
        access_log_class: type[aweb.AbstractAccessLogger] = aweb.AccessLogger,
        access_log_format: str = aweb.AccessLogger.LOG_FORMAT,
        access_log: ta.Optional[logging.Logger] = aweb.access_logger,
        handle_signals: bool = True,
        handler_cancellation: bool = False,
) -> None:
    async def wait(
            starting_tasks: "weakref.WeakSet[asyncio.Task[object]]", shutdown_timeout: float
    ) -> None:
        # Wait for pending tasks for a given time limit.
        t = asyncio.current_task()
        assert t is not None
        starting_tasks.add(t)
        with suppress(asyncio.TimeoutError):
            await asyncio.wait_for(_wait(starting_tasks), timeout=shutdown_timeout)

    async def _wait(exclude: "weakref.WeakSet[asyncio.Task[object]]") -> None:
        t = asyncio.current_task()
        assert t is not None
        exclude.add(t)
        while tasks := asyncio.all_tasks().difference(exclude):
            await asyncio.wait(tasks)

    # An internal function to actually do all dirty job for application running
    if asyncio.iscoroutine(app):
        app = await app

    app = ta.cast(aweb.Application, app)

    runner = aweb.AppRunner(
        app,
        handle_signals=handle_signals,
        access_log_class=access_log_class,
        access_log_format=access_log_format,
        access_log=access_log,
        keepalive_timeout=keepalive_timeout,
        shutdown_timeout=shutdown_timeout,
        handler_cancellation=handler_cancellation,
    )

    await runner.setup()
    # On shutdown we want to avoid waiting on tasks which run forever. It's very likely that all tasks which run forever
    # will have been created by the time we have completed the application startup (in runner.setup()), so we just
    # record all running tasks here and exclude them later.
    starting_tasks: "weakref.WeakSet[asyncio.Task[object]]" = weakref.WeakSet(asyncio.all_tasks())
    runner.shutdown_callback = functools.partial(wait, starting_tasks, shutdown_timeout)

    try:
        sites = make_sites(runner, sites_cfg)

        for site in sites:
            await site.start()

        if print:  # pragma: no branch
            names = sorted(str(s.name) for s in runner.sites)
            print(
                "======== Running on {} ========\n"
                "(Press CTRL+C to quit)".format(", ".join(names))
            )

        # sleep forever by 1 hour intervals,
        while True:
            await asyncio.sleep(3600)

    finally:
        await runner.cleanup()


def run_app(
        app: ta.Union[aweb.Application, ta.Awaitable[aweb.Application]],
        *,
        sites_cfg: SitesConfig = SitesConfig(),

        shutdown_timeout: float = 60.0,
        keepalive_timeout: float = 75.0,
        print: ta.Optional[ta.Callable[..., None]] = print,
        access_log_class: type[aweb.AbstractAccessLogger] = aweb.AccessLogger,
        access_log_format: str = aweb.AccessLogger.LOG_FORMAT,
        access_log: ta.Optional[logging.Logger] = aweb.access_logger,
        handle_signals: bool = True,
        handler_cancellation: bool = False,
        loop: ta.Optional[asyncio.AbstractEventLoop] = None,
) -> None:
    """Run an app locally"""
    if loop is None:
        loop = asyncio.new_event_loop()

    # Configure if and only if in debugging mode and using the default logger
    if loop.get_debug() and access_log and access_log.name == "aiohttp.access":
        if access_log.level == logging.NOTSET:
            access_log.setLevel(logging.DEBUG)
        if not access_log.hasHandlers():
            access_log.addHandler(logging.StreamHandler())

    main_task = loop.create_task(
        _run_app(
            app,

            sites_cfg=sites_cfg,

            shutdown_timeout=shutdown_timeout,
            keepalive_timeout=keepalive_timeout,
            print=print,
            access_log_class=access_log_class,
            access_log_format=access_log_format,
            access_log=access_log,
            handle_signals=handle_signals,
            handler_cancellation=handler_cancellation,
        )
    )

    try:
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main_task)
    except (aweb.GracefulExit, KeyboardInterrupt):  # pragma: no cover
        pass
    finally:
        _cancel_tasks({main_task}, loop)
        _cancel_tasks(asyncio.all_tasks(loop), loop)
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
