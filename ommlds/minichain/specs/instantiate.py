import typing as ta

from .types import ResolvedBackendSpec


##


def instantiate_backend_spec(rbs: ResolvedBackendSpec) -> ta.Any:
    def rec(cur: ResolvedBackendSpec) -> ta.Any:
        args: list[ta.Any] = []

        if (ch := cur.children) is None:
            pass
        elif isinstance(ch, tuple):
            args.append(tuple(rec(x) for x in ch))
        else:
            args.append(rec(ch))

        args.extend(cur.configs or ())

        return cur.ctor(*args)

    return rec(rbs)
