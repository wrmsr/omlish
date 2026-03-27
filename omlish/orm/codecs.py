import abc
import typing as ta

from .. import dataclasses as dc
from .. import lang


##


class Codec(lang.Abstract):
    @abc.abstractmethod
    def encode(self, obj: ta.Any) -> ta.Any:
        raise NotImplementedError

    @abc.abstractmethod
    def decode(self, obj: ta.Any) -> ta.Any:
        raise NotImplementedError


@dc.dataclass(frozen=True)
@dc.extra_class_params(override=True)
class FnCodec:
    encode: ta.Callable[[ta.Any], ta.Any]
    decode: ta.Callable[[ta.Any], ta.Any]
