# -*- coding: utf-8 -*-


import asyncio
import inspect
import os
import signal as _signal
import sys
import traceback

from asyncio import (
    AbstractEventLoop,
    StreamReader,
    StreamWriter,
)
from asyncio import Queue  # noqa: F401
from contextlib import contextmanager
from itertools import count
from unittest import mock
from typing import (
    Callable,
    Iterable,
    Iterator,
    Optional,
    TextIO,
    Tuple,
    Union,
)

from ._mempipe import mempipe


def call_with_minimal_args(f: Callable, **kwds):
    spec = inspect.signature(f)
    kwds = {
        k: kwds[k] for k, p in spec.parameters.items()
        if p.kind != inspect.Parameter.VAR_KEYWORD
    }
    return f(**kwds)


class OutputStreamAdapter(StreamWriter):
    """StreamWriter that wraps a file-like object."""

    def __init__(self, stream: TextIO) -> None:
        self._stream = stream

    def write(self, data: bytes) -> None:
        self._stream.write(data.decode('utf-8'))

    def writelines(self, lines: Iterable[bytes]) -> None:
        for line in lines:
            self._stream.write(line.decode('utf-8'))
            self._stream.write('\n')

    def can_write_eof(self) -> bool:
        return True

    # TODO: test this without closing the "real" sys.stdout!
    def write_eof(self) -> None:
        # self._stream.close()
        pass

    # NOTE: impossible to please `mypy` because documented signature is
    #       incomplete.
    async def drain(self):
        self._stream.flush()


class Process(object):
    """Mock for ``asyncio.subprocess.Process``."""

    def __init__(
            self,
            *,
            pid: int,
            run: Callable,
            argv=[],
            env=None,
            kwds={},
            stdin: Optional[int] = None,
            stdout: Union[int, TextIO, None] = None,
            stderr: Union[int, TextIO, None] = None,
            limit: Optional[int] = None,
            loop: Optional[AbstractEventLoop] = None,
    ) -> None:

        self._loop = loop or asyncio.get_event_loop()
        self._pid = pid
        self._stdin = None  # type: Optional[StreamWriter]
        self._stdout = None  # type: Optional[StreamReader]
        self._stderr = None  # type: Optional[StreamReader]

        # Handle standard input redirection.
        r_stdin = None  # Optional[StreamReader]
        if stdin == asyncio.subprocess.PIPE:
            r_stdin, self._stdin = mempipe(limit=limit, loop=loop)
        else:
            # TODO: wrap `sys.stdin` in a `StreamReader`.
            r_stdin, self._stdin = None, None

        # Handle standard output redirection.
        if stdout == asyncio.subprocess.PIPE:
            self._stdout, w_stdout = mempipe(limit=limit, loop=loop)
        else:
            stdout = stdout or sys.stdout
            assert stdout is not None
            assert not isinstance(stdout, int)
            self._stdout, w_stdout = None, OutputStreamAdapter(stdout)

        # Handle standard error redirection.
        if stderr == asyncio.subprocess.PIPE:
            self._stderr, w_stderr = mempipe(limit=limit, loop=loop)
        else:
            stderr = stderr or sys.stderr
            assert stderr is not None
            assert not isinstance(stderr, int)
            self._stderr, w_stderr = None, OutputStreamAdapter(stderr)

        # Mock signal handling.
        self._signals = asyncio.Queue()  # type: Queue

        # Start the application-defined process simulation.
        self._done = asyncio.Event(loop=loop)
        self._task = self._loop.create_task(self._run_wrapper(
            run,
            stdin=r_stdin,
            stdout=w_stdout,
            stderr=w_stderr,
            signals=self._signals,
            env=env or {k: v for k, v in os.environ.items()},
            argv=argv,
            kwds=kwds,
        ))

        # Keep a reference to the streams, we'll need them later.
        self._w_stdout = w_stdout
        self._w_stderr = w_stderr

        # Process exit code is undefined until the simulation completes.
        self._returncode = None  # type: Optional[int]

    async def _run_wrapper(
            self,
            run: Callable,
            *,
            stdout,
            stderr,
            **kwds,
    ) -> int:
        try:
            return await call_with_minimal_args(
                run,
                stdout=stdout,
                stderr=stderr,
                **kwds
            )
        except asyncio.CancelledError:
            return 1
        finally:
            await stdout.drain()
            await stderr.drain()
            self._done.set()

    @property
    def pid(self) -> int:
        return self._pid

    @property
    def stdin(self) -> Optional[StreamWriter]:
        return self._stdin

    @property
    def stdout(self) -> Optional[StreamReader]:
        return self._stdout

    @property
    def stderr(self) -> Optional[StreamReader]:
        return self._stderr

    async def wait(self) -> int:
        await asyncio.wait({self._task})
        await self._done.wait()
        e = self._task.exception()
        if e is None:
            r = self._task.result()
            if r is None:
                r = 0
            self._returncode = r
        else:
            # Format traceback and send it to stderr (as if it had been printed
            # in the child process' output).
            self._w_stderr.writelines(
                line.encode('utf-8')
                for line in traceback.format_exception(
                    e.__class__, e, e.__traceback__
                )
            )
            self._returncode = 1
        assert self._w_stdout
        assert self._w_stderr
        self._w_stdout.write_eof()
        self._w_stderr.write_eof()
        return self._returncode

    async def communicate(self, input: bytes=b'') -> Tuple[Optional[bytes], Optional[bytes]]:
        if self._stdin:
            self._stdin.write(input)
            self._stdin.write_eof()
        await self.wait()
        stdout = None
        if self._stdout:
            stdout = await self._stdout.read()
        stderr = None
        if self._stderr:
            stderr = await self._stderr.read()
        return stdout, stderr

    def send_signal(self, signal: int) -> None:
        self._signals.put_nowait(signal)

    def terminate(self) -> None:
        self._task.cancel()

    def kill(self) -> None:
        if sys.platform == 'win32':
            self.terminate()
        else:
            # NOTE: for a real process, we'd send SIGKILL, which would then be
            #       passed as SIGINT to the application, but we don't have a
            #       kernel to make that substution here.
            self.send_signal(_signal.SIGINT)

    @property
    def returncode(self) -> Optional[int]:
        return self._returncode


@contextmanager
def mock_subprocess(
        run: Callable,
        loop: Optional[AbstractEventLoop] = None,
) -> Iterator[None]:
    """Calls ``run()`` instead of spawning a sub-process.

    :param run: A coroutine function that simulates the sub-process.  Can
     return ``None`` or ``0`` to simulate successful process execution or a
     non-zero error code to simulate sub-process terminate with a non-zero exit
     code.  If an exception is raised, the result is 1 (non-zero).  This
     function can accept a variable number of arguments, see below.

    Dependency injection is used with the ``run()`` coroutine function to pass
    only arguments that are declared in the function's signature.  Omit all but
    the arguments you intend to use.  Here are all the available arguments:

    - ``argv``: a list of strings passed as positional arguments to
      ``asyncio.create_subprocess_exec()``.
    - ``stdin``: an ``asyncio.StreamReader`` instance.  When output is not
      redirected, this reads from the "real" ``sys.stdin``.
    - ``stdout``: an ``asyncio.StreamWriter`` instance.  When output is not
      redirected, this writes to the "real" ``sys.stdout``.
    - ``stderr``: an ``asyncio.StreamWriter`` instance.  When output is not
      redirected, this writes to the "real" ``sys.stderr``.
    - ``env``: a ``dict`` containing environment variables passed to
      ``asyncio.create_subprocess_exec()``.
    - ``signals``: an ``asyncio.Queue`` object that receives integers passed to
      ``asyncio.Process.send_signal()``.
    - ``kwds``: extra keyword arguments passed to
      ``asyncio.create_subprocess_exec()``.

    .. versionadded:: 0.1

    """

    loop = loop or asyncio.get_event_loop()

    pid = count(start=1)

    def create_subprocess_exec(
            *args,
            stdin=None,
            stdout=None,
            env=None,
            stderr=None,
            loop=None,
            limit=None,
            **kwds,
    ):
        """Mock for ``asyncio.create_subprocess_exec()``."""
        loop = loop or asyncio.get_event_loop()
        f = asyncio.Future()
        process = Process(
            pid=next(pid),
            run=run,
            loop=loop,
            argv=list(args),
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
            env=env,
            limit=limit,
            kwds=kwds,
        )
        loop.call_soon(f.set_result, process)
        return f

    with mock.patch('asyncio.create_subprocess_exec', create_subprocess_exec):
        yield None
