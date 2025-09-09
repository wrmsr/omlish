# @omlish-lite
"""
binding language:
 - .bind() more restrictive
 - .log() more lax - if passed a tv-type already in bindings it won't automatically create a default

TODO:
 - bind() *requires* types, the funcs don't ?
 - hidden / keyless items? retrievable by type?
  - kind of 'context' shit, a separate layer
   - TypedLoggerContext
 - provider helpers
  - default classmethod on the item class?
  - cvar / tls binder
 - stdlib LogRecord adaptation
 - rendering overrides
  - by type, on the type, 'injected', ...
 - explicit None vs omit
 - KeyedTypedLoggerValue?
 - kwargs! but forced to the end
 - loggers, at least stdlib, are necessarily mutable - @contextlib.contextmanager def contextual()?

lol ok:
 - (k, v)
  - first pos arg is special
   - if 2-ple, raise if is a TypedLogger thingy
 - type[TypedLoggerValue]
 - TypedLoggerValueProvider

https://docs.python.org/3/library/typing.html#user-defined-generic-types
"""
import dataclasses as dc
import logging
import typing as ta
import unittest

from ..bindings import FullTypedLoggerBindings
from ..bindings import TypedLoggerValueWrapper
from ..types import DefaultTypedLoggerValue
from ..types import MultiTypedLoggerValue
from ..types import TypedLoggerValue
from .api import DEFAULT_TYPED_LOGGER_BINDINGS
from .api import TypedLogger


log = logging.getLogger(__name__)


##


class Tag(TypedLoggerValue[str]):
    _default_key = True


class Tags(MultiTypedLoggerValue[ta.AbstractSet[str]]):
    # FIXME:
    # _default_key = True

    @classmethod
    def merge_values(cls, *values: ta.AbstractSet[str]) -> ta.AbstractSet[str]:
        return frozenset(e for s in values for e in s)


@dc.dataclass(frozen=True)
class Thingy:
    s: str


class ThingyTlv(TypedLoggerValue[Thingy]):
    _default_key = 'thingy'


class Thingy2Tlv(DefaultTypedLoggerValue[str]):
    _default_key = 'thingy2'

    @classmethod
    def _default_value(cls, thingy: 'ThingyTlv') -> str:
        return thingy.v.s + ' - 2'


class TestTyped(unittest.TestCase):
    def test_typed(self):
        # logs.configure_standard_logging()
        log.info('hi')

        tlog = TypedLogger(FullTypedLoggerBindings(
            DEFAULT_TYPED_LOGGER_BINDINGS,
            TypedLoggerValueWrapper({Thingy}, ThingyTlv),
        ))

        for _ in range(2):
            tlog.info(
                'hi',
                Tag('some tag'),
                ('foo', 'bar'),
                Thingy('wrap me'),  # type: ignore
                Thingy2Tlv,
                Tags({'a tags'}),
                Tags({'b tags'}),
                barf=True,
            )

            tlog.info('abcd')
            tlog.info(('abc %d efg', 420))

            tlog.info(lambda: 'abcd')
            tlog.info(Tag('some tag'))
            tlog.info(lambda: Tag('some tag'))
            tlog.info(lambda: [Tag('some tag')])
            tlog.info(lambda: ['hi', Tag('some tag')])
