import typing as ta

from .types import ResolvedBackendSpec


##


def instantiate_backend_spec(rbs: ResolvedBackendSpec, *args: ta.Any, **kwargs: ta.Any) -> ta.Any:
    def rec(cur: ResolvedBackendSpec) -> ta.Any:
        cur_args: list[ta.Any] = []

        if (ch := cur.children) is None:
            pass
        elif isinstance(ch, tuple):
            cur_args.append(tuple(rec(x) for x in ch))
        else:
            cur_args.append(rec(ch))

        cur_args.extend(cur.configs or ())

        return cur.ctor(
            *cur_args,
            *(args if ch is None else ()),
            **(kwargs if ch is None else {}),
        )

    return rec(rbs)
