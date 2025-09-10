import sys as _sys
import typing as _ta

from .. import lang as _lang  # noqa


with _lang.auto_proxy_init(globals()):
    ##

    from .asyncs import (  # noqa
        AbstractAsyncSubprocesses,
    )

    from .base import (  # noqa
        SubprocessChannelOption,

        VerboseCalledProcessError,
        BaseSubprocesses,
    )

    from .maysync import (  # noqa
        MaysyncSubprocesses,
    )

    from .run import (  # noqa
        SubprocessRunOutput,
        SubprocessRun,
        SubprocessRunnable,
    )

    from .sync import (  # noqa
        AbstractSubprocesses,

        Subprocesses,

        subprocesses,
    )

    from .utils import (  # noqa
        subprocess_close as close,
    )

    from .wrap import (  # noqa
        subprocess_shell_wrap_exec as shell_wrap_exec,
        subprocess_maybe_shell_wrap_exec as maybe_shell_wrap_exec,
    )


##


if _ta.TYPE_CHECKING:
    from . import sync as _sync  # noqa
else:
    _sync = _lang.proxy_import('.sync', __package__)


def run(
        *cmd: str,
        input: _ta.Any = None,  # noqa
        timeout: '_lang.TimeoutLike' = None,
        check: bool = False,
        capture_output: bool | None = None,
        **kwargs: _ta.Any,
) -> 'SubprocessRunOutput':
    return _sync.subprocesses.run(
        *cmd,
        input=input,
        timeout=timeout,
        check=check,
        capture_output=capture_output,
        **kwargs,
    )


def check_call(
        *cmd: str,
        stdout: _ta.Any = _sys.stderr,
        **kwargs: _ta.Any,
) -> None:
    return _sync.subprocesses.check_call(
        *cmd,
        stdout=stdout,
        **kwargs,
    )


def check_output(
        *cmd: str,
        **kwargs: _ta.Any,
) -> bytes:
    return _sync.subprocesses.check_output(
        *cmd,
        **kwargs,
    )


def check_output_str(
        *cmd: str,
        **kwargs: _ta.Any,
) -> str:
    return _sync.subprocesses.check_output_str(
        *cmd,
        **kwargs,
    )


def try_call(
        *cmd: str,
        **kwargs: _ta.Any,
) -> bool:
    return _sync.subprocesses.try_call(
        *cmd,
        **kwargs,
    )


def try_output(
        *cmd: str,
        **kwargs: _ta.Any,
) -> bytes | None:
    return _sync.subprocesses.try_output(
        *cmd,
        **kwargs,
    )


def try_output_str(
        *cmd: str,
        **kwargs: _ta.Any,
) -> str | None:
    return _sync.subprocesses.try_output_str(
        *cmd,
        **kwargs,
    )
