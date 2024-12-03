import abc
import codecs
import dataclasses as dc
import functools
import typing as ta

from omlish import check
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
    def iterencode(self) -> ta.Generator[I, O | None, None]:
        raise NotImplementedError

    @abc.abstractmethod
    def iterdecode(self) -> ta.Generator[O, I | None, None]:
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

    new: ta.Callable[..., EagerCodec]
    new_incremental: ta.Callable[..., IncrementalCodec] | None = None


##


TextEncodingErrors: ta.TypeAlias = ta.Literal[
    # Raise UnicodeError (or a subclass), this is the default. Implemented in strict_errors().
    'strict',

    # Ignore the malformed data and continue without further notice. Implemented in ignore_errors().
    'ignore',

    # Replace with a replacement marker. On encoding, use ? (ASCII character). On decoding, use � (U+FFFD, the official
    # REPLACEMENT CHARACTER). Implemented in replace_errors().
    'replace',

    # Replace with backslashed escape sequences. On encoding, use hexadecimal form of Unicode code point with formats
    # \xhh \uxxxx \Uxxxxxxxx. On decoding, use hexadecimal form of byte value with format \xhh. Implemented in
    # backslashreplace_errors().
    'backslashreplace',

    # On decoding, replace byte with individual surrogate code ranging from U+DC80 to U+DCFF. This code will then be
    # turned back into the same byte when the 'surrogateescape' error handler is used when encoding the data. (See PEP
    # 383 for more.)
    'surrogateescape',

    # The following error handlers are only applicable to encoding (within text encodings):

    # Replace with XML/HTML numeric character reference, which is a decimal form of Unicode code point with format
    # &#num;. Implemented in xmlcharrefreplace_errors().
    'xmlcharrefreplace',

    # Replace with \N{...} escape sequences, what appears in the braces is the Name property from Unicode Character
    # Database. Implemented in namereplace_errors().
    'namereplace',

    # In addition, the following error handler is specific to the given codecs:
    # utf-8, utf-16, utf-32, utf-16-be, utf-16-le, utf-32-be, utf-32-le

    # Allow encoding and decoding surrogate code point (U+D800 - U+DFFF) as normal code point. Otherwise these codecs
    # treat the presence of surrogate code point in str as an error.
    'surrogatepass',
]


@dc.dataclass(frozen=True, kw_only=True)
class TextEncodingOptions:
    errors: TextEncodingErrors = 'strict'


class TextEncodingComboCodec(ComboCodec[str, bytes]):
    def __init__(
            self,
            info: codecs.CodecInfo,
            options: TextEncodingOptions = TextEncodingOptions(),
    ) -> None:
        super().__init__()
        self._info = info
        self._opts = options

    @classmethod
    def lookup(
            cls,
            name: str,
            options: TextEncodingOptions = TextEncodingOptions(),
    ) -> 'TextEncodingComboCodec':
        return cls(codecs.lookup(name), options)

    def encode(self, i: str) -> bytes:
        o, _ = self._info.encode(i, self._opts.errors)
        return o

    def decode(self, o: bytes) -> str:
        i, _ = self._info.decode(o, self._opts.errors)
        return i

    def iterencode(self) -> ta.Generator[str, bytes | None, None]:
        x = self._info.incrementalencoder(self._opts.errors)
        i = yield
        while True:
            if not i:
                break
            o = x.encode(i)
            i = yield o
        o = x.encode(i, final=True)
        yield o

    def iterdecode(self) -> ta.Generator[bytes, str | None, None]:
        x = self._info.incrementaldecoder(self._opts.errors)
        i = yield
        while True:
            if not i:
                break
            o = x.decode(i)
            i = yield o
        o = x.decode(i, final=True)
        yield o


def normalize_encoding_name(s: str) -> str:
    if ' ' in s:
        raise NameError(s)
    return s.lower().replace('_', '-')


def make_text_encoding_codec(
        name: str,
        aliases: ta.Collection[str] | None = None,
) -> Codec:
    return Codec(
        name=check.equal(name, normalize_encoding_name(name)),
        aliases=check.not_isinstance(aliases, str),

        input=str,
        output=bytes,

        new=functools.partial(TextEncodingComboCodec.lookup, name),
        new_incremental=functools.partial(TextEncodingComboCodec.lookup, name),
    )


ASCII = make_text_encoding_codec('ascii', ['646', 'us-ascii'])
LATIN1 = make_text_encoding_codec('latin-1', ['iso-8859-1', 'iso8859-1', '8859', 'cp819', 'latin', 'latin1', 'l1'])
UTF32 = make_text_encoding_codec('utf-32', ['u32', 'utf32'])
UTF32BE = make_text_encoding_codec('utf-32-be', ['utf-32be'])
UTF32LE = make_text_encoding_codec('utf-32-le', ['utf-32le'])
UTF16 = make_text_encoding_codec('utf-16', ['u16', 'utf16'])
UTF16BE = make_text_encoding_codec('utf-16-be', ['utf-16be'])
UTF16LE = make_text_encoding_codec('utf-16-le', ['utf-16le'])
UTF7 = make_text_encoding_codec('utf-7', ['u7', 'unicode-1-1-utf-7'])
UTF8 = make_text_encoding_codec('utf-8', ['u8', 'utf', 'utf8', 'cp65001'])
UTF8SIG = make_text_encoding_codec('utf-8-sig')


##


def _main() -> None:
    assert UTF8.new().encode('hi') == b'hi'
    assert UTF8.new(TextEncodingOptions(errors='ignore')).encode('hi') == b'hi'

    g = check.not_none(UTF8.new_incremental)().iterencode()
    next(g)
    print(g.send('hi'))
    print(g.send(''))

    g = check.not_none(UTF8.new_incremental)().iterdecode()
    next(g)
    print(g.send(b'hi'))
    print(g.send(b''))


if __name__ == '__main__':
    _main()

