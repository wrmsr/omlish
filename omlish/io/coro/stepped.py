import typing as ta

from ... import check
from ... import lang
from ..buffers import ReadableListBuffer
from .consts import DEFAULT_BUFFER_SIZE
from .direct import BytesDirectCoro
from .direct import StrDirectCoro


T = ta.TypeVar('T')

O = ta.TypeVar('O')
I = ta.TypeVar('I')
R = ta.TypeVar('R')

OF = ta.TypeVar('OF')
OT = ta.TypeVar('OT')


# Stepped coros accept a non-None input, then in response yield zero or more non-None outputs, until yielding None to
# signal they need more input again.
SteppedCoro: ta.TypeAlias = ta.Generator[O | None, I | None, R]

# Conventionally, these are sent and themselves yield an empty value to signify termination.
BytesSteppedCoro: ta.TypeAlias = SteppedCoro[bytes, bytes, R]
StrSteppedCoro: ta.TypeAlias = SteppedCoro[str, str, R]

BytesToStrSteppedCoro: ta.TypeAlias = SteppedCoro[str, bytes, R]
StrToBytesSteppedCoro: ta.TypeAlias = SteppedCoro[bytes, str, R]


# Stepped reader generators emit either an int or None to request input, or emit some other kind of output.
SteppedReaderCoro: ta.TypeAlias = ta.Generator[int | None | O, I | None, R]

BytesSteppedReaderCoro: ta.TypeAlias = SteppedReaderCoro[bytes, bytes, R]
StrSteppedReaderCoro: ta.TypeAlias = SteppedReaderCoro[str, str, R]


##


@lang.autostart
def flatmap_stepped_coro(
        fn: ta.Callable[[list[OF]], OT],
        g: SteppedCoro[OF, I, R],
        *,
        terminate: ta.Callable[[OF], bool] | None = None,
) -> ta.Generator[OT, I, lang.Maybe[R]]:
    """
    Given a stepped coro and a function taking a list, returns a direct (1:1) coro which accepts input, builds a list of
    yielded coro output, calls the given function with that list, and yields the result.

    An optional terminate function may be provided which will cause this function to return early if it returns true for
    an encountered yielded value. The encountered value causing termination will be included in the list sent to the
    given fn.

    Returns a Maybe of either the given coro's return value or empty if the terminator was encountered.
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


def joined_bytes_stepped_coro(g: BytesSteppedCoro[R]) -> BytesDirectCoro[R]:
    return flatmap_stepped_coro(_join_bytes, g, terminate=_is_empty)


def joined_str_stepped_coro(g: StrSteppedCoro[R]) -> StrDirectCoro[R]:
    return flatmap_stepped_coro(_join_str, g, terminate=_is_empty)


##


def read_into_bytes_stepped_coro(
        g: BytesSteppedCoro,
        f: ta.IO,
        *,
        read_size: int = DEFAULT_BUFFER_SIZE,
) -> ta.Iterator[bytes]:
    yield from lang.genmap(  # type: ignore[misc]
        joined_bytes_stepped_coro(g),
        lang.readiter(f, read_size),
    )


def read_into_str_stepped_coro(
        g: StrSteppedCoro,
        f: ta.TextIO,
        *,
        read_size: int = DEFAULT_BUFFER_SIZE,
) -> ta.Iterator[str]:
    yield from lang.genmap(
        joined_str_stepped_coro(g),
        lang.readiter(f, read_size),
    )


##


@lang.autostart
def buffer_bytes_stepped_reader_coro(g: BytesSteppedReaderCoro) -> BytesSteppedCoro:
    i: bytes | None
    o = g.send(None)
    rlb = ReadableListBuffer()
    eof = False

    while True:
        if eof:
            raise EOFError

        if not len(rlb):
            if (more := check.isinstance((yield None), bytes)):
                rlb.feed(more)
            else:
                eof = True

        if o is None:
            i = check.not_none(rlb.read())

        elif isinstance(o, int):
            while len(rlb) < o:
                more = check.isinstance((yield None), bytes)
                if not more:
                    raise EOFError
                # FIXME: lol - share guts with readers
                rlb.feed(more)

            i = check.not_none(rlb.read(o))

        else:
            raise TypeError(o)

        while True:
            o = g.send(i)
            i = None
            if isinstance(o, bytes):
                check.none((yield o))
                if not o:
                    return
            else:
                break
