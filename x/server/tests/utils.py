import typing as ta

import pytest

from omlish.diag import pydevd as pdu

from .. import headers


T = ta.TypeVar('T')


##


DEFAULT_TIMEOUT_S: float = 50


def get_timeout_s() -> float | None:
    if pdu.is_present():
        return None
    else:
        return DEFAULT_TIMEOUT_S


##


def get_exception_chain(ex: BaseException) -> list[BaseException]:
    cur: BaseException | None = ex
    ret: list[BaseException] = []
    while cur is not None:
        ret.append(cur)
        cur = cur.__cause__
    return ret


CONNECTION_REFUSED_EXCEPTION_TYPES: tuple[type[Exception], ...] = (
    # Note: This *is* an OSError, it's here for switchability and explicitness.
    ConnectionRefusedError,

    OSError,
)


def is_connection_refused_exception(e: Exception) -> bool:
    return any(isinstance(ce, ConnectionRefusedError) for ce in get_exception_chain(e))


##


@pytest.fixture(autouse=True)
def headers_time_patch(monkeypatch) -> None:
    monkeypatch.setattr(headers, '_now', lambda: 5000)
