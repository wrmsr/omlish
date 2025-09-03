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

from omlish.logs import all as logs

from ..bindings import TypedLoggerValueWrapper
from ..bindings import TypedLoggerBindings
from ..types import DefaultTypedLoggerValue
from ..types import TypedLoggerValue


log = logging.getLogger(__name__)


##


class Tag(TypedLoggerValue[str]):
    _default_key = True


@dc.dataclass(frozen=True)
class Thingy:
    s: str


class ThingyTlv(TypedLoggerValue[Thingy]):
    _default_key = 'thingy'


class Thingy2Tlv(DefaultTypedLoggerValue[str]):
    _default_key = 'thingy2'

    @classmethod
    def _default_value(cls, thingy: ThingyTlv) -> str:
        return thingy.v.s + ' - 2'


def test_typed():
    # l = TypedLoggerImpl(TypedLoggerValueNamespace(
    #     Tag('foo'),
    #     ThreadId(420),
    #     TimeProvider,
    # ))
    # l.log(10)
    # l.log(10, 'hi', Tag('bar'))
    # l.log(10, ('hi',), Tag('bar'))

    # bl: list = [
    #     # TimeNs(420),
    #     Time,
    #     ('foo', 'bar'),
    #     # Tag,
    #     ('other_tag', Tag),
    # ]
    # bsl: list = [
    #     Level(logging.INFO),
    #     *as_typed_logger_bindings(*bl),
    #     *build_default_provider_typed_logger_bindings(*bl),
    #     *build_default_key_field_typed_logger_bindings(*bl),
    #     Tag('some tag'),
    # ]
    # bs = TypedLoggerBindings(*bsl)
    # ctx = TypedLoggerContext(bs)
    # print()
    # for k, fv in ctx.bindings.key_map.items():
    #     print((k, ctx.resolve_field_value(fv)))
    # print()
    #
    # bs2 = TypedLoggerBindings(bs, Tag('hi'), override=True)
    # ctx2 = TypedLoggerContext(bs2)
    # print(ctx2[Tag])
    # print(ctx.bindings.key_map)
    #
    # # TODO: args to bindings items - Time -> Time.default()

    logs.configure_standard_logging()
    log.info('hi')

    from ..api import DEFAULT_TYPED_LOGGER_BINDINGS  # noqa
    from ..api import TypedLoggerImpl  # noqa

    slog = TypedLoggerImpl(TypedLoggerBindings(
        DEFAULT_TYPED_LOGGER_BINDINGS,
        TypedLoggerValueWrapper({Thingy}, ThingyTlv),
    ))

    slog.log(
        logging.INFO,
        'hi',
        Tag('some tag'),
        ('foo', 'bar'),
        Thingy('wrap me'),  # type: ignore
        Thingy2Tlv,
        barf=True,
    )

    slog.log(logging.INFO, 'abcd')
    slog.log(logging.INFO, ('abc %d efg', 420))
