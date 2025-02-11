# ruff: noqa: UP006 UP007
# @omlish-lite
import abc
import contextlib
import logging
import os
import subprocess
import time
import typing as ta

from ..lite.timeouts import Timeout
from .wrap import subprocess_maybe_shell_wrap_exec


T = ta.TypeVar('T')
SubprocessChannelOption = ta.Literal['pipe', 'stdout', 'devnull']  # ta.TypeAlias


##


# Valid channel type kwarg values:
#  - A special flag negative int
#  - A positive fd int
#  - A file-like object
#  - None

SUBPROCESS_CHANNEL_OPTION_VALUES: ta.Mapping[SubprocessChannelOption, int] = {
    'pipe': subprocess.PIPE,
    'stdout': subprocess.STDOUT,
    'devnull': subprocess.DEVNULL,
}


##


class VerboseCalledProcessError(subprocess.CalledProcessError):
    @classmethod
    def from_std(cls, e: subprocess.CalledProcessError) -> 'VerboseCalledProcessError':
        return cls(
            e.returncode,
            e.cmd,
            output=e.output,
            stderr=e.stderr,
        )

    def __str__(self) -> str:
        msg = super().__str__()
        if self.output is not None:
            msg += f' Output: {self.output!r}'
        if self.stderr is not None:
            msg += f' Stderr: {self.stderr!r}'
        return msg


class BaseSubprocesses(abc.ABC):  # noqa
    DEFAULT_LOGGER: ta.ClassVar[ta.Optional[logging.Logger]] = None

    def __init__(
            self,
            *,
            log: ta.Optional[logging.Logger] = None,
            try_exceptions: ta.Optional[ta.Tuple[ta.Type[Exception], ...]] = None,
    ) -> None:
        super().__init__()

        self._log = log if log is not None else self.DEFAULT_LOGGER
        self._try_exceptions = try_exceptions if try_exceptions is not None else self.DEFAULT_TRY_EXCEPTIONS

    def set_logger(self, log: ta.Optional[logging.Logger]) -> None:
        self._log = log

    #

    def prepare_args(
            self,
            *cmd: str,
            env: ta.Optional[ta.Mapping[str, ta.Any]] = None,
            extra_env: ta.Optional[ta.Mapping[str, ta.Any]] = None,
            quiet: bool = False,
            shell: bool = False,
            **kwargs: ta.Any,
    ) -> ta.Tuple[ta.Tuple[ta.Any, ...], ta.Dict[str, ta.Any]]:
        if self._log:
            self._log.debug('Subprocesses.prepare_args: cmd=%r', cmd)
            if extra_env:
                self._log.debug('Subprocesses.prepare_args: extra_env=%r', extra_env)

        #

        if extra_env:
            env = {**(env if env is not None else os.environ), **extra_env}

        #

        if quiet and 'stderr' not in kwargs:
            if self._log and not self._log.isEnabledFor(logging.DEBUG):
                kwargs['stderr'] = subprocess.DEVNULL

        for chk in ('stdout', 'stderr'):
            try:
                chv = kwargs[chk]
            except KeyError:
                continue
            kwargs[chk] = SUBPROCESS_CHANNEL_OPTION_VALUES.get(chv, chv)

        #

        if not shell:
            cmd = subprocess_maybe_shell_wrap_exec(*cmd)

        #

        if 'timeout' in kwargs:
            kwargs['timeout'] = Timeout.of(kwargs['timeout']).or_(None)

        #

        return cmd, dict(
            env=env,
            shell=shell,
            **kwargs,
        )

    @contextlib.contextmanager
    def wrap_call(
            self,
            *cmd: ta.Any,
            raise_verbose: bool = False,
            **kwargs: ta.Any,
    ) -> ta.Iterator[None]:
        start_time = time.time()
        try:
            if self._log:
                self._log.debug('Subprocesses.wrap_call.try: cmd=%r', cmd)

            yield

        except Exception as exc:  # noqa
            if self._log:
                self._log.debug('Subprocesses.wrap_call.except: exc=%r', exc)

            if (
                    raise_verbose and
                    isinstance(exc, subprocess.CalledProcessError) and
                    not isinstance(exc, VerboseCalledProcessError) and
                    (exc.output is not None or exc.stderr is not None)
            ):
                raise VerboseCalledProcessError.from_std(exc) from exc

            raise

        finally:
            end_time = time.time()
            elapsed_s = end_time - start_time

            if self._log:
                self._log.debug('Subprocesses.wrap_call.finally: elapsed_s=%f cmd=%r', elapsed_s, cmd)

    @contextlib.contextmanager
    def prepare_and_wrap(
            self,
            *cmd: ta.Any,
            raise_verbose: bool = False,
            **kwargs: ta.Any,
    ) -> ta.Iterator[ta.Tuple[
        ta.Tuple[ta.Any, ...],
        ta.Dict[str, ta.Any],
    ]]:
        cmd, kwargs = self.prepare_args(*cmd, **kwargs)

        with self.wrap_call(
                *cmd,
                raise_verbose=raise_verbose,
                **kwargs,
        ):
            yield cmd, kwargs

    #

    DEFAULT_TRY_EXCEPTIONS: ta.Tuple[ta.Type[Exception], ...] = (
        FileNotFoundError,
        subprocess.CalledProcessError,
    )

    def try_fn(
            self,
            fn: ta.Callable[..., T],
            *cmd: str,
            try_exceptions: ta.Optional[ta.Tuple[ta.Type[Exception], ...]] = None,
            **kwargs: ta.Any,
    ) -> ta.Union[T, Exception]:
        if try_exceptions is None:
            try_exceptions = self._try_exceptions

        try:
            return fn(*cmd, **kwargs)

        except try_exceptions as e:  # noqa
            if self._log and self._log.isEnabledFor(logging.DEBUG):
                self._log.exception('command failed')
            return e

    async def async_try_fn(
            self,
            fn: ta.Callable[..., ta.Awaitable[T]],
            *cmd: ta.Any,
            try_exceptions: ta.Optional[ta.Tuple[ta.Type[Exception], ...]] = None,
            **kwargs: ta.Any,
    ) -> ta.Union[T, Exception]:
        if try_exceptions is None:
            try_exceptions = self._try_exceptions

        try:
            return await fn(*cmd, **kwargs)

        except try_exceptions as e:  # noqa
            if self._log and self._log.isEnabledFor(logging.DEBUG):
                self._log.exception('command failed')
            return e
