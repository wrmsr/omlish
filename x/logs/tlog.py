# @omlish-amalg ./_tlog.py
# @omlish-lite
import dataclasses as dc
import logging

from omlish.logs.typed.bindings import FullTypedLoggerBindings
from omlish.logs.typed.bindings import TypedLoggerValueWrapper
from omlish.logs.typed.tests.api import DEFAULT_TYPED_LOGGER_BINDINGS
from omlish.logs.typed.tests.api import TypedLogger
from omlish.logs.typed.types import DefaultTypedLoggerValue
from omlish.logs.typed.types import TypedLoggerValue


##


@dc.dataclass(frozen=True)
class Thingy:
    s: str


class LoggerValues:
    class Tag(TypedLoggerValue[str]):
        _default_key = True

    class Thingy_(TypedLoggerValue[Thingy]):  # noqa
        _default_key = 'thingy'

    class Thingy2(DefaultTypedLoggerValue[str]):
        _default_key = True

        @classmethod
        def _default_value(cls, thingy: 'LoggerValues.Thingy_') -> str:
            return thingy.v.s + ' - 2'


def _main() -> None:
    tlog = TypedLogger(FullTypedLoggerBindings(
        DEFAULT_TYPED_LOGGER_BINDINGS,
        TypedLoggerValueWrapper({Thingy}, LoggerValues.Thingy_),
    ))

    for _ in range(2):
        tlog.log(
            logging.INFO,
            'hi',
            LoggerValues.Tag('some tag'),
            ('foo', 'bar'),
            Thingy('wrap me'),  # type: ignore
            LoggerValues.Thingy2,
            barf=True,
        )

        tlog.log(logging.INFO, 'abcd')
        tlog.log(logging.INFO, ('abc %d efg', 420))


if __name__ == '__main__':
    _main()
