import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import reflect as rfl


AnySignal: ta.TypeAlias = ta.Union[
    'Signal',
    'SignalRequest',
    'SignalResponse',
]

InSignalT = ta.TypeVar('InSignalT', bound='Signal')
OutSignalT = ta.TypeVar('OutSignalT', bound='Signal')

T = ta.TypeVar('T')


##


@dc.dataclass(frozen=True)
class Signal(lang.Abstract):
    pass


##


class SignalInOut(lang.Abstract, lang.Sealed, ta.Generic[InSignalT, OutSignalT]):
    @property
    def _IO(self) -> tuple[type[InSignalT], type[OutSignalT]]:  # noqa
        try:
            return self.__dict__['_IO']
        except KeyError:
            pass

        oty = rfl.get_orig_class(self)
        check.in_(ta.get_origin(oty), (SignalRequest, SignalResponse))
        i_ty, o_ty = ta.get_args(oty)
        ret = (check.issubclass(i_ty, Signal), check.issubclass(o_ty, Signal))

        self.__dict__['_IO'] = ret
        return ret

    @property
    def I(self) -> type[InSignalT]:  # noqa
        return self._IO[0]

    @property
    def O(self) -> type[OutSignalT]:  # noqa
        return self._IO[1]


@ta.final
@dc.dataclass(frozen=True, eq=False)
@dc.extra_class_params(repr_id=True, allow_dynamic_dunder_attrs=True)
class SignalRequest(SignalInOut[InSignalT, OutSignalT], lang.Final):
    i: InSignalT

    def respond(self, o: OutSignalT) -> 'SignalResponse[InSignalT, OutSignalT]':
        # FIXME: durably cache GenericAlias somehow
        return SignalResponse[self.I, self.O](self, o)  # noqa


@ta.final
@dc.dataclass(frozen=True, eq=False)
@dc.extra_class_params(repr_id=True, allow_dynamic_dunder_attrs=True)
class SignalResponse(SignalInOut[InSignalT, OutSignalT], lang.Final):
    q: SignalRequest[InSignalT, OutSignalT]
    o: OutSignalT

    @property
    def i(self) -> InSignalT:
        return self.q.i


##


@ta.final
@dc.dataclass(frozen=True, eq=False)
class AnySignalWithSender(lang.Final, ta.Generic[T]):
    m: AnySignal
    x: T


##


ANY_SIGNAL_TYPES: tuple[type[AnySignal], ...] = (
    Signal,
    SignalRequest,
    SignalResponse,
)


def unwrap_any_signal(m: AnySignal | AnySignalWithSender[T]) -> AnySignal:
    if isinstance(m, ANY_SIGNAL_TYPES):
        return m
    elif isinstance(m, AnySignalWithSender):
        return m.m
    else:
        raise TypeError(m)
