import collections.abc
import typing as ta


K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


def yield_dict_init(*args: ta.Any, **kwargs: ta.Any) -> ta.Iterable[tuple[ta.Any, ta.Any]]:
    if len(args) > 1:
        raise TypeError
    if args:
        [src] = args
        if isinstance(src, collections.abc.Mapping):
            for k in src:
                yield (k, src[k])
        else:
            for k, v in src:
                yield (k, v)
    for k, v in kwargs.items():
        yield (k, v)


def merge_dicts(
        *dcts: ta.Mapping[K, V],
        pair_fn: ta.Callable[[K, V], tuple[K, V] | None] | None = None,
        conflict_fn: ta.Callable[[K, V, V], tuple[K, V] | None] | None = None,
) -> dict[K, V]:
    out: dict[K, V] = {}

    for d in dcts:
        for k_v in d.items():
            if pair_fn is not None and (k_v := pair_fn(*k_v)) is None:  # type: ignore[assignment]
                continue

            k, v = k_v
            if k in out:
                if conflict_fn is None:
                    raise KeyError(k)

                if (k_v := conflict_fn(k, out[k], v)) is None:  # type: ignore[assignment]
                    continue
                k, v = k_v

            out[k] = v

    return out
