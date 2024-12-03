import abc
import codecs
import dataclasses as dc
import functools
import typing as ta

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
    def iterencode(self) -> ta.Generator[I | None, O | None, None]:
        raise NotImplementedError

    @abc.abstractmethod
    def iterdecode(self) -> ta.Generator[O | None, I | None, None]:
        raise NotImplementedError


class ComboCodec(  # noqa
    EagerCodec[I, O],
    IncrementalCodec[I, O],
    lang.Abstract,
    ta.Generic[I, O],
):
    pass


##


@dc.dataclass(frozen=True, kw_only=True)
class Codec(lang.Final):
    name: str
    aliases: ta.Collection[str] | None = None

    input: rfl.Type
    output: rfl.Type

    options: type | None = None

    new: ta.Callable[..., EagerCodec] | None = None
    new_incremental: ta.Callable[..., IncrementalCodec] | None = None


##


@dc.dataclass(frozen=True, kw_only=True)
class TextCodecOptions:
    errors: str = 'strict'


class TextComboCodec(EagerCodec[str, bytes]):
    def __init__(self, info: codecs.CodecInfo, options: TextCodecOptions = TextCodecOptions()) -> None:
        super().__init__()
        self._info = info
        self._opts = options

    @classmethod
    def lookup(cls, name: str, options: TextCodecOptions = TextCodecOptions()) -> 'TextComboCodec':
        return cls(codecs.lookup(name), options)

    def encode(self, i: str) -> bytes:
        o, _ = self._info.encode(i, self._opts.errors)
        return o

    def decode(self, o: bytes) -> str:
        i, _ = self._info.decode(o, self._opts.errors)
        return i

    def iterencode(self) -> ta.Generator[I | None, O | None, None]:
        raise NotImplementedError

    def iterdecode(self) -> ta.Generator[O | None, I | None, None]:
        raise NotImplementedError


def make_text_encoding_codec(
        name: str,
        *,
        aliases: ta.Collection[str] | None = None,
) -> Codec:
    def new(options: TextCodecOptions = TextCodecOptions()) -> EagerCodec:
        return TextComboCodec(codecs.lookup(name), options)

    return Codec(
        name=name,
        aliases=aliases,

        input=str,
        output=bytes,

        new=functools.partial(TextComboCodec.lookup, name),
        new_incremental=functools.partial(TextComboCodec.lookup, name),
    )


UTF8 = make_text_encoding_codec('utf8', aliases=['utf-8'])


def _main() -> None:
    assert UTF8.new().encode('hi') == b'hi'


if __name__ == '__main__':
    _main()

