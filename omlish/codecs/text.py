import codecs
import dataclasses as dc
import functools
import typing as ta

from .. import check
from .base import Codec
from .base import ComboCodec
from .standard import STANDARD_CODECS


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

    ##
    # The following error handlers are only applicable to encoding (within text encodings):

    # Replace with XML/HTML numeric character reference, which is a decimal form of Unicode code point with format
    # &#num;. Implemented in xmlcharrefreplace_errors().
    'xmlcharrefreplace',

    # Replace with \N{...} escape sequences, what appears in the braces is the Name property from Unicode Character
    # Database. Implemented in namereplace_errors().
    'namereplace',

    ##
    # In addition, the following error handler is specific to the given codecs: utf-8, utf-16, utf-32, utf-16-be,
    # utf-16-le, utf-32-be, utf-32-le

    # Allow encoding and decoding surrogate code point (U+D800 - U+DFFF) as normal code point. Otherwise these codecs
    # treat the presence of surrogate code point in str as an error.
    'surrogatepass',
]


@dc.dataclass(frozen=True, kw_only=True)
class TextEncodingOptions:
    errors: TextEncodingErrors = 'strict'


##


class TextEncodingComboCodec(ComboCodec[str, bytes]):
    def __init__(
            self,
            info: codecs.CodecInfo,
            options: TextEncodingOptions = TextEncodingOptions(),
    ) -> None:
        super().__init__()

        self._info = check.isinstance(info, codecs.CodecInfo)
        self._opts = check.isinstance(options, TextEncodingOptions)

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

    def encode_incremental(self) -> ta.Generator[bytes | None, str]:
        x = self._info.incrementalencoder(self._opts.errors)
        i = yield None
        while True:
            if not i:
                break
            o = x.encode(i)
            i = yield o or None
        o = x.encode(i, final=True)
        yield o

    def decode_incremental(self) -> ta.Generator[str | None, bytes]:
        x = self._info.incrementaldecoder(self._opts.errors)
        i = yield None
        while True:
            if not i:
                break
            o = x.decode(i)
            i = yield o or None
        o = x.decode(i, final=True)
        yield o


##


class TextEncodingCodec(Codec):
    pass


def normalize_text_encoding_name(s: str) -> str:
    if ' ' in s:
        raise NameError(s)
    return s.lower().replace('_', '-')


def make_text_encoding_codec(
        name: str,
        aliases: ta.Sequence[str] | None = None,
        *,
        append_to: ta.MutableSequence[Codec] | None = None,
) -> TextEncodingCodec:
    codec = TextEncodingCodec(
        name=check.equal(name, normalize_text_encoding_name(name)),
        aliases=check.not_isinstance(aliases, str),

        input=str,
        output=bytes,

        new=functools.partial(TextEncodingComboCodec.lookup, name),
        new_incremental=functools.partial(TextEncodingComboCodec.lookup, name),
    )

    if append_to is not None:
        append_to.append(codec)

    return codec


##


ASCII = make_text_encoding_codec(
    'ascii',
    ['646', 'us-ascii'],
    append_to=STANDARD_CODECS,
)

LATIN1 = make_text_encoding_codec(
    'latin-1',
    ['iso-8859-1', 'iso8859-1', '8859', 'cp819', 'latin', 'latin1', 'l1'],
    append_to=STANDARD_CODECS,
)

UTF32 = make_text_encoding_codec(
    'utf-32',
    ['u32', 'utf32'],
    append_to=STANDARD_CODECS,
)

UTF32BE = make_text_encoding_codec(
    'utf-32-be',
    ['utf-32be'],
    append_to=STANDARD_CODECS,
)

UTF32LE = make_text_encoding_codec(
    'utf-32-le',
    ['utf-32le'],
    append_to=STANDARD_CODECS,
)

UTF16 = make_text_encoding_codec(
    'utf-16',
    ['u16', 'utf16'],
    append_to=STANDARD_CODECS,
)

UTF16BE = make_text_encoding_codec(
    'utf-16-be',
    ['utf-16be'],
    append_to=STANDARD_CODECS,
)

UTF16LE = make_text_encoding_codec(
    'utf-16-le',
    ['utf-16le'],
    append_to=STANDARD_CODECS,
)

UTF7 = make_text_encoding_codec(
    'utf-7',
    ['u7', 'unicode-1-1-utf-7'],
    append_to=STANDARD_CODECS,
)

UTF8 = make_text_encoding_codec(
    'utf-8',
    ['u8', 'utf', 'utf8', 'cp65001'],
    append_to=STANDARD_CODECS,
)

UTF8SIG = make_text_encoding_codec(
    'utf-8-sig',
    append_to=STANDARD_CODECS,
)
