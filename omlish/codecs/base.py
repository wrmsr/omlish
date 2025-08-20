"""
TODO:
 - bytes-like - bytearray, memoryview
 - FileCodec
 - implement options
"""
import abc
import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang
from .. import reflect as rfl
from ..funcs import pairs as fps
from ..manifests.base import ModAttrManifest


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

    def as_pair(self) -> fps.FnPair[I, O]:
        return fps.of(self.encode, self.decode)


class IncrementalCodec(lang.Abstract, ta.Generic[I, O]):
    @abc.abstractmethod
    def encode_incremental(self) -> ta.Generator[O | None, I]:
        raise NotImplementedError

    @abc.abstractmethod
    def decode_incremental(self) -> ta.Generator[I | None, O]:
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
    aliases: ta.Sequence[str] | None = dc.xfield(
        default=None,
        coerce=lang.opt_fn(lambda s: [check_codec_name(a) for a in s]),
    )

    input: rfl.Type = dc.xfield(coerce=rfl.type_)
    output: rfl.Type = dc.xfield(coerce=rfl.type_)

    options: type | None = None

    new: ta.Callable[..., EagerCodec]
    new_incremental: ta.Callable[..., IncrementalCodec] | None = None


##


@dc.dataclass(frozen=True, kw_only=True)
class LazyLoadedCodec(ModAttrManifest):
    name: str
    aliases: ta.Sequence[str] | None = None

    @classmethod
    def new(
            cls,
            module: str,
            attr: str,
            codec: Codec,
    ) -> 'LazyLoadedCodec':
        return cls(
            module=module,
            attr=attr,
            name=codec.name,
            aliases=codec.aliases,
        )
