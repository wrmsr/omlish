import typing as ta

from ... import check
from ... import lang
from .consts import DEFAULT_BUFFER_SIZE
from .direct import BytesDirectGenerator
from .direct import StrDirectGenerator


T = ta.TypeVar('T')

O = ta.TypeVar('O')
I = ta.TypeVar('I')
R = ta.TypeVar('R')

OF = ta.TypeVar('OF')
OT = ta.TypeVar('OT')


# Stepped generators accept a non-None input, then in response yield zero or more non-None outputs, until yielding None
# to signal they need more input again.
SteppedGenerator: ta.TypeAlias = ta.Generator[O | None, I | None, R]

# Conventionally, these are sent and themselves yield an empty value to signify termination.
BytesSteppedGenerator: ta.TypeAlias = SteppedGenerator[bytes, bytes, R]
StrSteppedGenerator: ta.TypeAlias = SteppedGenerator[str, str, R]

BytesToStrSteppedGenerator: ta.TypeAlias = SteppedGenerator[str, bytes, R]
StrToBytesSteppedGenerator: ta.TypeAlias = SteppedGenerator[bytes, str, R]


# Stepped reader generators emit either an int or None to request input, or emit some other kind of output.
SteppedReaderGenerator: ta.TypeAlias = ta.Generator[int | None | O, I | None, R]

BytesSteppedReaderGenerator: ta.TypeAlias = SteppedReaderGenerator[bytes, bytes, R]
StrSteppedReaderGenerator: ta.TypeAlias = SteppedReaderGenerator[str, str, R]


##


@lang.autostart
def flatmap_stepped_generator(
        fn: ta.Callable[[list[OF]], OT],
        g: SteppedGenerator[OF, I, R],
        *,
        terminate: ta.Callable[[OF], bool] | None = None,
) -> ta.Generator[OT, I, lang.Maybe[R]]:
    """
    Given a stepped generator and a function taking a list, returns a direct (1:1) generator which accepts input, builds
    a list of yielded generator output, calls the given function with that list, and yields the result.

    An optional terminate function may be provided which will cause this function to return early if it returns true for
    an encountered yielded value. The encountered value causing termination will be included in the list sent to the
    given fn.

    Returns a Maybe of either the given generator's return value or empty if the terminator was encountered.
    """

    l: list[OF]
    i: I | None = yield  # type: ignore
    while True:
        l = []

        while True:
            try:
                o = g.send(i)
            except StopIteration as e:
                if l:
                    yield fn(l)
                return lang.just(e.value)

            i = None

            if o is None:
                break

            l.append(o)

            if terminate is not None and terminate(o):
                yield fn(l)
                return lang.empty()

        i = yield fn(l)


##


def _join_bytes(l: ta.Sequence[bytes]) -> bytes:
    if not l:
        return b''
    elif len(l) == 1:
        return l[0]
    else:
        return b''.join(l)


def _join_str(l: ta.Sequence[str]) -> str:
    if not l:
        return ''
    elif len(l) == 1:
        return l[0]
    else:
        return ''.join(l)


def _is_empty(o: T) -> bool:
    return len(o) < 1  # type: ignore


def joined_bytes_stepped_generator(g: BytesSteppedGenerator[R]) -> BytesDirectGenerator[R]:
    return flatmap_stepped_generator(_join_bytes, g, terminate=_is_empty)


def joined_str_stepped_generator(g: StrSteppedGenerator[R]) -> StrDirectGenerator[R]:
    return flatmap_stepped_generator(_join_str, g, terminate=_is_empty)


##


def read_into_bytes_stepped_generator(
        g: BytesSteppedGenerator,
        f: ta.IO,
        *,
        read_size: int = DEFAULT_BUFFER_SIZE,
) -> ta.Iterator[bytes]:
    yield from lang.genmap(  # type: ignore[misc]
        joined_bytes_stepped_generator(g),
        lang.readiter(f, read_size),
    )


def read_into_str_stepped_generator(
        g: StrSteppedGenerator,
        f: ta.TextIO,
        *,
        read_size: int = DEFAULT_BUFFER_SIZE,
) -> ta.Iterator[str]:
    yield from lang.genmap(
        joined_str_stepped_generator(g),
        lang.readiter(f, read_size),
    )


##


@lang.autostart
def buffer_bytes_stepped_reader_generator(g: BytesSteppedReaderGenerator) -> BytesSteppedGenerator:
    o = g.send(None)
    buf: ta.Any = None

    while True:
        if not buf:
            buf = check.isinstance((yield None), bytes)

        if o is None or not buf:
            i = buf
        elif isinstance(o, int):
            if len(buf) < o:
                raise NotImplementedError
            i = buf[:o]
            buf = buf[o:]
        else:
            raise TypeError(o)

        while True:
            o = g.send(i)
            i = None
            if isinstance(o, bytes):
                check.none((yield o))
            else:
                break
