import os.path
import typing as ta

from ....std.subprocesses import subprocess_check_output
from ....std.logging import log


DEFAULT_CMD_TRY_EXCEPTIONS: ta.AbstractSet[ta.Type[Exception]] = frozenset([
    FileNotFoundError,
])


def cmd(
        cmd: ta.Union[str, ta.Sequence[str]],
        *,
        try_: ta.Union[bool, ta.Iterable[ta.Type[Exception]]] = False,
        env: ta.Optional[ta.Mapping[str, str]] = None,
        **kwargs,
) -> ta.Optional[str]:
    log.debug(cmd)
    if env:
        log.debug(env)

    env = {**os.environ, **(env or {})}

    es: tuple[ta.Type[Exception], ...] = (Exception,)
    if isinstance(try_, bool):
        if try_:
            es = tuple(DEFAULT_CMD_TRY_EXCEPTIONS)
    elif try_:
        es = tuple(try_)
        try_ = True

    try:
        buf = subprocess_check_output(cmd, env=env, **kwargs)
    except es:
        if try_:
            log.exception('cmd failed: %r', cmd)
            return None
        else:
            raise

    out = buf.decode('utf-8').strip()
    log.debug(out)
    return out
