"""
TODO:
 - bytes-like - bytearray, memoryview
"""
import abc
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import reflect as rfl


I = ta.TypeVar('I')
O = ta.TypeVar('O')


##


class EagerCodec(lang.Abstract, ta.Generic[I, O]):
    @abc.abstractmethod
    def encode(self, i: I) -> O:
        raise NotImplementedError

    @abc.abstractmethod
    def decode(self, o: O) -> I:
        raise NotImplementedError


class IncrementalCodec(lang.Abstract, ta.Generic[I, O]):
    @abc.abstractmethod
    def encode_incremental(self) -> ta.Generator[O | None, I, None]:
        raise NotImplementedError

    @abc.abstractmethod
    def decode_incremental(self) -> ta.Generator[I | None, O, None]:
        raise NotImplementedError


class ComboCodec(  # noqa
    EagerCodec[I, O],
    IncrementalCodec[I, O],
    lang.Abstract,
    ta.Generic[I, O],
):
    pass


##


def check_codec_name(s: str) -> str:
    check.non_empty_str(s)
    check.not_in('_', s)
    check.equal(s.strip(), s)
    return s


##


@dc.dataclass(frozen=True, kw_only=True)
class Codec:
    name: str = dc.xfield(coerce=check_codec_name)
    aliases: ta.Collection[str] | None = dc.xfield(
        default=None,
        coerce=lang.opt_fn(lambda s: [check_codec_name(a) for a in s]),  # type: ignore
    )

    input: rfl.Type = dc.xfield(coerce=rfl.type_)
    output: rfl.Type = dc.xfield(coerce=rfl.type_)

    options: type | None = None

    new: ta.Callable[..., EagerCodec]
    new_incremental: ta.Callable[..., IncrementalCodec] | None = None


##


@dc.dataclass(frozen=True, kw_only=True)
class LazyLoadedCodec:
    mod_name: str
    attr_name: str
    name: str
    aliases: ta.Collection[str] | None = None

    @classmethod
    def new(
            cls,
            mod_name: str,
            attr_name: str,
            codec: Codec,
    ) -> 'LazyLoadedCodec':
        return cls(
            mod_name=mod_name,
            attr_name=attr_name,
            name=codec.name,
            aliases=codec.aliases,
        )
