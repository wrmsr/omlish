# ruff: noqa: UP006 UP007
import contextlib
import logging
import os
import shlex
import subprocess
import sys
import time
import typing as ta

from .logs import log
from .runtime import is_debugger_attached


T = ta.TypeVar('T')
SubprocessChannelOption = ta.Literal['pipe', 'stdout', 'devnull']


##


SUBPROCESS_CHANNEL_OPTION_VALUES: ta.Mapping[SubprocessChannelOption, int] = {
    'pipe': subprocess.PIPE,
    'stdout': subprocess.STDOUT,
    'devnull': subprocess.DEVNULL,
}


##


_SUBPROCESS_SHELL_WRAP_EXECS = False


def subprocess_shell_wrap_exec(*args: str) -> ta.Tuple[str, ...]:
    return ('sh', '-c', ' '.join(map(shlex.quote, args)))


def subprocess_maybe_shell_wrap_exec(*args: str) -> ta.Tuple[str, ...]:
    if _SUBPROCESS_SHELL_WRAP_EXECS or is_debugger_attached():
        return subprocess_shell_wrap_exec(*args)
    else:
        return args


def prepare_subprocess_invocation(
        *args: str,
        env: ta.Optional[ta.Mapping[str, ta.Any]] = None,
        extra_env: ta.Optional[ta.Mapping[str, ta.Any]] = None,
        quiet: bool = False,
        shell: bool = False,
        **kwargs: ta.Any,
) -> ta.Tuple[ta.Tuple[ta.Any, ...], ta.Dict[str, ta.Any]]:
    log.debug('prepare_subprocess_invocation: args=%r', args)
    if extra_env:
        log.debug('prepare_subprocess_invocation: extra_env=%r', extra_env)

    if extra_env:
        env = {**(env if env is not None else os.environ), **extra_env}

    if quiet and 'stderr' not in kwargs:
        if not log.isEnabledFor(logging.DEBUG):
            kwargs['stderr'] = subprocess.DEVNULL

    if not shell:
        args = subprocess_maybe_shell_wrap_exec(*args)

    return args, dict(
        env=env,
        shell=shell,
        **kwargs,
    )


##


@contextlib.contextmanager
def subprocess_common_context(*args: ta.Any, **kwargs: ta.Any) -> ta.Iterator[None]:
    start_time = time.time()
    try:
        log.debug('subprocess_common_context.try: args=%r', args)
        yield

    except Exception as exc:  # noqa
        log.debug('subprocess_common_context.except: exc=%r', exc)
        raise

    finally:
        end_time = time.time()
        elapsed_s = end_time - start_time
        log.debug('subprocess_common_context.finally: elapsed_s=%f args=%r', elapsed_s, args)


##


def subprocess_check_call(
        *args: str,
        stdout: ta.Any = sys.stderr,
        **kwargs: ta.Any,
) -> None:
    args, kwargs = prepare_subprocess_invocation(*args, stdout=stdout, **kwargs)
    with subprocess_common_context(*args, **kwargs):
        return subprocess.check_call(args, **kwargs)  # type: ignore


def subprocess_check_output(
        *args: str,
        **kwargs: ta.Any,
) -> bytes:
    args, kwargs = prepare_subprocess_invocation(*args, **kwargs)
    with subprocess_common_context(*args, **kwargs):
        return subprocess.check_output(args, **kwargs)


def subprocess_check_output_str(*args: str, **kwargs: ta.Any) -> str:
    return subprocess_check_output(*args, **kwargs).decode().strip()


##


DEFAULT_SUBPROCESS_TRY_EXCEPTIONS: ta.Tuple[ta.Type[Exception], ...] = (
    FileNotFoundError,
    subprocess.CalledProcessError,
)


def _subprocess_try_run(
        fn: ta.Callable[..., T],
        *args: ta.Any,
        try_exceptions: ta.Tuple[ta.Type[Exception], ...] = DEFAULT_SUBPROCESS_TRY_EXCEPTIONS,
        **kwargs: ta.Any,
) -> ta.Union[T, Exception]:
    try:
        return fn(*args, **kwargs)
    except try_exceptions as e:  # noqa
        if log.isEnabledFor(logging.DEBUG):
            log.exception('command failed')
        return e


def subprocess_try_call(
        *args: str,
        try_exceptions: ta.Tuple[ta.Type[Exception], ...] = DEFAULT_SUBPROCESS_TRY_EXCEPTIONS,
        **kwargs: ta.Any,
) -> bool:
    if isinstance(_subprocess_try_run(
            subprocess_check_call,
            *args,
            try_exceptions=try_exceptions,
            **kwargs,
    ), Exception):
        return False
    else:
        return True


def subprocess_try_output(
        *args: str,
        try_exceptions: ta.Tuple[ta.Type[Exception], ...] = DEFAULT_SUBPROCESS_TRY_EXCEPTIONS,
        **kwargs: ta.Any,
) -> ta.Optional[bytes]:
    if isinstance(ret := _subprocess_try_run(
            subprocess_check_output,
            *args,
            try_exceptions=try_exceptions,
            **kwargs,
    ), Exception):
        return None
    else:
        return ret


def subprocess_try_output_str(*args: str, **kwargs: ta.Any) -> ta.Optional[str]:
    out = subprocess_try_output(*args, **kwargs)
    return out.decode().strip() if out is not None else None


##


def subprocess_close(
        proc: subprocess.Popen,
        timeout: ta.Optional[float] = None,
) -> None:
    # TODO: terminate, sleep, kill
    if proc.stdout:
        proc.stdout.close()
    if proc.stderr:
        proc.stderr.close()
    if proc.stdin:
        proc.stdin.close()

    proc.wait(timeout)
