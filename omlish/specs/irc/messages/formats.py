import enum
import typing as ta

from .... import check
from .... import dataclasses as dc
from .... import lang
from ....funcs import pairs as fps


MessageParamsUnpacker: ta.TypeAlias = fps.FnPair[
    ta.Mapping[str, str],  # params
    ta.Mapping[str, ta.Any],  # kwargs
]


##


class MessageFormat(dc.Frozen, final=True):
    name: str

    class Param(dc.Case):
        @classmethod
        def of(cls, obj: ta.Any) -> 'MessageFormat.Param':
            if isinstance(obj, MessageFormat.Param):
                return obj

            elif isinstance(obj, str):
                s = check.non_empty_str(obj)

                optional = False
                if s.startswith('?'):
                    optional = True
                    s = s[1:]

                arity = MessageFormat.KwargParam.Arity.SINGLE
                if s.startswith('*'):
                    arity = MessageFormat.KwargParam.Arity.VARIADIC
                    s = s[1:]

                elif s.startswith(','):
                    arity = MessageFormat.KwargParam.Arity.COMMA_LIST
                    s = s[1:]

                return MessageFormat.KwargParam(
                    s,
                    optional=optional,
                    arity=arity,
                )

            else:
                raise TypeError(obj)

    class KwargParam(Param):
        name: str = dc.xfield(validate=lang.is_ident)

        optional: bool = False

        class Arity(enum.Enum):
            SINGLE = enum.auto()  # <foo>
            VARIADIC = enum.auto()  # <foo>{ <foo>}
            COMMA_LIST = enum.auto()  # <foo>{,<foo>}

        arity: Arity = Arity.SINGLE

    class LiteralParam(Param):
        text: str

    params: ta.Sequence[Param]

    _: dc.KW_ONLY

    unpack_params: MessageParamsUnpacker | None = None

    @dc.init
    def _validate_params(self) -> None:
        kws = [p for p in self.params if isinstance(p, MessageFormat.KwargParam)]
        check.unique(p.name for p in kws)
        check.state(all(p.arity is not MessageFormat.KwargParam.Arity.VARIADIC for p in kws[:-1]))

    @classmethod
    def of(
            cls,
            name: str,
            *params: ta.Any,
            **kwargs: ta.Any,
    ) -> 'MessageFormat':
        return cls(
            name,
            [MessageFormat.Param.of(p) for p in params],
            **kwargs,
        )
