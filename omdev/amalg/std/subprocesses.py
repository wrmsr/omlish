# ruff: noqa: UP006 UP007
import logging
import os
import subprocess
import sys
import typing as ta

from .logs import log


##


def _prepare_subprocess_invocation(
        *args: ta.Any,
        env: ta.Optional[ta.Mapping[str, ta.Any]] = None,
        extra_env: ta.Optional[ta.Mapping[str, ta.Any]] = None,
        **kwargs: ta.Any,
) -> ta.Tuple[ta.Tuple[ta.Any, ...], ta.Dict[str, ta.Any]]:
    log.debug(args)
    if extra_env:
        log.debug(extra_env)

    if extra_env:
        env = {**(env if env is not None else os.environ), **extra_env}

    return args, dict(
        env=env,
        **kwargs,
    )


def subprocess_check_call(*args: ta.Any, stdout=sys.stderr, **kwargs) -> None:
    args, kwargs = _prepare_subprocess_invocation(*args, stdout=stdout, **kwargs)
    return subprocess.check_call(args, **kwargs)  # type: ignore


def subprocess_check_output(*args: ta.Any, **kwargs) -> bytes:
    args, kwargs = _prepare_subprocess_invocation(*args, **kwargs)
    return subprocess.check_output(args, **kwargs)


##


DEFAULT_SUBPROCESS_TRY_EXCEPTIONS: ta.Tuple[ta.Type[Exception], ...] = (
    FileNotFoundError,
    subprocess.CalledProcessError,
)


def subprocess_try_call(
        *args: ta.Any,
        try_exceptions: ta.Tuple[ta.Type[Exception], ...] = DEFAULT_SUBPROCESS_TRY_EXCEPTIONS,
        **kwargs,
) -> bool:
    try:
        subprocess_check_call(*args, **kwargs)
    except try_exceptions as e:  # noqa
        if log.isEnabledFor(logging.DEBUG):
            log.exception('command failed')
        return False
    else:
        return True


def subprocess_try_output(
        *args: ta.Any,
        try_exceptions: ta.Tuple[ta.Type[Exception], ...] = DEFAULT_SUBPROCESS_TRY_EXCEPTIONS,
        **kwargs,
) -> ta.Optional[bytes]:
    try:
        return subprocess_check_output(*args, **kwargs)
    except try_exceptions as e:  # noqa
        if log.isEnabledFor(logging.DEBUG):
            log.exception('command failed')
        return None
