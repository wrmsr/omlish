import abc
import codecs
import typing as ta

from .. import check
from .. import defs
from .. import lang
from .types import Codec
from .types import Encoder
from .types import Decoder


F = ta.TypeVar('F')
T = ta.TypeVar('T')


class Nop(Codec, lang.Final):

    defs.repr()

    def encode(self, obj: F) -> T:
        return obj

    def decode(self, obj: T) -> F:
        return obj


def nop():
    return Nop()


class _CompositeEncoder(Encoder, metaclass=abc.ABCMeta):

    @abc.abstractproperty
    def encoders(self) -> ta.Sequence[Encoder]:
        raise NotImplementedError

    def encode(self, o):
        for encoder in self.encoders:
            o = encoder.encode(o)
        return o


class _CompositeDecoder(Decoder, metaclass=abc.ABCMeta):

    @abc.abstractproperty
    def decoders(self) -> ta.Sequence[Decoder]:
        raise NotImplementedError

    def decode(self, o):
        for decoder in reversed(self.decoders):
            o = decoder.decode(o)
        return o


class CompositeEncoder(_CompositeEncoder, Encoder, lang.Final):

    def __init__(self, *encoders: Encoder) -> None:
        super().__init__()

        self._encoders = encoders
        for e in encoders:
            check.not_none(e)

    @property
    def encoders(self):
        return self._encoders


class CompositeDecoder(_CompositeDecoder, Decoder, lang.Final):

    def __init__(self, *decoders: Decoder) -> None:
        super().__init__()

        self._decoders = decoders
        for d in decoders:
            check.not_none(d)

    @property
    def decoders(self):
        return self._decoders


class CompositeCodec(_CompositeEncoder, _CompositeDecoder, Codec, lang.Final):

    def __init__(self, *codecs: Codec) -> None:
        super().__init__()

        self._codecs = codecs
        for c in codecs:
            check.not_none(c)

    defs.repr('codecs')

    @property
    def codecs(self) -> ta.Sequence[Codec]:
        return self._codecs

    @property
    def encoders(self) -> ta.Sequence[Encoder]:
        return self.codecs

    @property
    def decoders(self) -> ta.Sequence[Decoder]:
        return self.codecs


composite = CompositeCodec


class InvertedCodec(Codec[F, T], lang.Final):

    def __init__(self, codec: Codec[T, F]) -> None:
        super().__init__()

        self._codec = check.not_none(codec)

    defs.repr('codec')

    @property
    def codec(self) -> Codec:
        return self._codec

    def encode(self, o: F) -> T:
        return self._codec.decode(o)

    def decode(self, o: T) -> F:
        return self._codec.encode(o)


inverted = InvertedCodec


class StandardCodec(Codec[F, T], lang.Final):

    def __init__(
            self,
            encoding: str,
            encode_errors: str = 'strict',
            decode_errors: str = 'strict',
    ) -> None:
        super().__init__()

        self._encoding = check.not_empty(encoding)
        self._encode_errors = encode_errors
        self._decode_errors = decode_errors

        self._codec = codecs.lookup(self._encoding)

    defs.repr('encoding', 'encode_errors', 'decode_errors')

    @property
    def encoding(self) -> str:
        return self._encoding

    @property
    def encode_errors(self) -> str:
        return self._encode_errors

    @property
    def decode_errors(self) -> str:
        return self._decode_errors

    def encode(self, o: F) -> T:
        encoded, consumed = self._codec.encode(o, self._encode_errors)
        return encoded

    def decode(self, o: T) -> F:
        decoded, consumed = self._codec.decode(o, self._decode_errors)
        return decoded


standard = StandardCodec


class FunctionPairCodec(Codec[F, T], lang.Final):

    def __init__(
            self,
            encode_fn: ta.Callable[[F], T],
            decode_fn: ta.Callable[[T], F],
    ):
        super().__init__()

        self._encode_fn = check.callable(encode_fn)
        self._decode_fn = check.callable(decode_fn)

    defs.repr('encode_fn', 'decode_fn')

    @property
    def encode_fn(self) -> ta.Callable[[F], T]:
        return self._encode_fn

    @property
    def decode_fn(self) -> ta.Callable[[T], F]:
        return self._decode_fn

    def encode(self, o: F) -> T:
        return self._encode_fn(o)

    def decode(self, o: T) -> F:
        return self._decode_fn(o)


function_pair = FunctionPairCodec


def symmetric(
        fn: ta.Callable[[T], T],
) -> FunctionPairCodec[T, T]:
    return FunctionPairCodec(
        fn,
        fn,
    )


class NullSafeCodec(Codec[ta.Optional[F], ta.Optional[T]], lang.Final):

    def __init__(self, codec: Codec[F, T]) -> None:
        super().__init__()

        self._codec = codec

    defs.repr('codec')

    @property
    def codec(self) -> Codec[F, T]:
        return self._codec

    def encode(self, obj: ta.Optional[F]) -> ta.Optional[T]:
        if obj is None:
            return None
        else:
            return self.codec.encode(obj)

    def decode(self, obj: ta.Optional[T]) -> ta.Optional[F]:
        if obj is None:
            return None
        else:
            return self.codec.decode(obj)


null_safe = NullSafeCodec


Wrapper = ta.Callable[[ta.Callable, ta.Any], ta.Any]


class WrappedCodec(Codec[ta.Optional[F], ta.Optional[T]], lang.Final):

    def __init__(
            self,
            wrapper: Wrapper,
            codec: Codec,
    ) -> None:
        super().__init__()

        self._wrapper = check.callable(wrapper)
        self._codec = check.not_none(codec)

    defs.repr('wrapper', 'codec')

    @property
    def wrapper(self) -> Wrapper:
        return self._wrapper

    @property
    def codec(self) -> Codec:
        return self._codec

    def encode(self, obj):
        return self._wrapper(self.codec._encode, obj)

    def decode(self, obj):
        return self._wrapper(self.codec._decode, obj)


wrapped = WrappedCodec
