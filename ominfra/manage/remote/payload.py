# ruff: noqa: UP006 UP007 UP045
import inspect
import sys
import typing as ta

from omlish.lite.cached import cached_nullary


RemoteExecutionPayloadFile = ta.NewType('RemoteExecutionPayloadFile', str)


##


@cached_nullary
def _get_self_src() -> str:
    return inspect.getsource(sys.modules[__name__])


def _is_src_amalg(src: str) -> bool:
    for l in src.splitlines():  # noqa
        if l.startswith('# @omlish-amalg-output '):
            return True
    return False


@cached_nullary
def _is_self_amalg() -> bool:
    return _is_src_amalg(_get_self_src())


def get_remote_payload_src(
        *,
        file: ta.Optional[RemoteExecutionPayloadFile],
) -> str:
    if file is not None:
        with open(file) as f:
            return f.read()

    if _is_self_amalg():
        return _get_self_src()

    import importlib.resources
    return importlib.resources.files(__package__.split('.')[0] + '.scripts').joinpath('manage.py').read_text()
