import typing as ta


##


def opt_repr(o: ta.Any) -> str | None:
    return repr(o) if o is not None else None


def truthy_repr(o: ta.Any) -> str | None:
    return repr(o) if o else None
