import typing as ta

from omlish import c3
from omlish import reflect as rfl


T = ta.TypeVar('T')


def find_impl(
        cls: rfl.Type,
        registry: ta.Mapping[rfl.Type, T],
) -> T | None:
    mro = c3.compose_mro(cls, registry.keys())

    match: type | None = None
    for t in mro:
        if match is not None:
            # If *match* is an implicit ABC but there is another unrelated, equally matching implicit ABC, refuse the
            # temptation to guess.
            if (
                    t in registry
                    and t not in cls.__mro__
                    and match not in cls.__mro__
                    and not issubclass(match, t)
            ):
                raise RuntimeError(f'Ambiguous dispatch: {match} or {t}')
            break

        if t in registry:
            match = t

    if match is None:
        return None
    return registry.get(match)


