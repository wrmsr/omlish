"""
TODO:
 - options / kwargs
"""
import base64
import binascii
import typing as ta

from .. import check
from .base import Codec
from .funcs import FnPairEagerCodec
from .standard import STANDARD_CODECS


##


class BytesCodec(Codec):
    pass


def make_bytes_encoding_codec(
        name: str,
        aliases: ta.Collection[str] | None,
        encode: ta.Callable[[bytes], bytes],
        decode: ta.Callable[[bytes], bytes],
        *,
        append_to: ta.MutableSequence[Codec] | None = None,
) -> BytesCodec:
    codec = BytesCodec(
        name=name,
        aliases=check.not_isinstance(aliases, str),

        input=bytes,
        output=bytes,

        new=lambda: FnPairEagerCodec.of(encode, decode),
    )

    if append_to is not None:
        append_to.append(codec)

    return codec


##


ASCII85 = make_bytes_encoding_codec(
    'ascii85',
    ['a85'],
    base64.a85encode,
    base64.a85decode,
    append_to=STANDARD_CODECS,
)

BASE16 = make_bytes_encoding_codec(
    'base16',
    ['b16'],
    base64.b16encode,
    base64.b16decode,
    append_to=STANDARD_CODECS,
)

BASE32 = make_bytes_encoding_codec(
    'base32',
    ['b32'],
    base64.b32encode,
    base64.b32decode,
    append_to=STANDARD_CODECS,
)

BASE64 = make_bytes_encoding_codec(
    'base64',
    ['b64'],
    base64.b64encode,
    base64.b64decode,
    append_to=STANDARD_CODECS,
)

BASE85 = make_bytes_encoding_codec(
    'base85',
    ['b85'],
    base64.b85encode,
    base64.b85decode,
    append_to=STANDARD_CODECS,
)

BASE32_HEX = make_bytes_encoding_codec(
    'base32-hex',
    ['b32-hex'],
    base64.b32hexencode,
    base64.b32hexdecode,
    append_to=STANDARD_CODECS,
)

BASE64_HEX = make_bytes_encoding_codec(
    'base64-hex',
    ['b64-hex'],
    base64.standard_b64encode,
    base64.standard_b64decode,
    append_to=STANDARD_CODECS,
)

BASE64_URLSAFE = make_bytes_encoding_codec(
    'base64-urlsafe',
    ['b64-urlsafe'],
    base64.urlsafe_b64encode,
    base64.urlsafe_b64decode,
    append_to=STANDARD_CODECS,
)

HEX = make_bytes_encoding_codec(
    'hex',
    [],
    binascii.b2a_hex,
    binascii.a2b_hex,
    append_to=STANDARD_CODECS,
)
