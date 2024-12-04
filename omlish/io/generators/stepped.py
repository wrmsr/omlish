import typing as ta

from ... import lang


I = ta.TypeVar('I')
OF = ta.TypeVar('OF')
OT = ta.TypeVar('OT')
R = ta.TypeVar('R')


@lang.autostart
def flatmap_stepped_generator(
        fn: ta.Callable[[list[OF]], OT],
        g: ta.Generator[OF | None, I | None, R],
        *,
        terminate: ta.Callable[[OF], bool] | None = None,
) -> ta.Generator[OT, I, lang.Maybe[R]]:
    """
    Given a 'stepped generator' - a generator which accepts input items and yields zero or more non-None values in
    response until it signals it's ready for the next input by yielding None - and a function taking a list, returns a
    1:1 generator which accepts input, builds a list of yielded generator output, calls the given function with that
    list, and yields the result.

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
