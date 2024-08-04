import typing as ta


def maybe_post_init(sup: ta.Any) -> bool:
    try:
        fn = sup.__post_init__
    except AttributeError:
        return False
    fn()
    return True


def opt_repr(o: ta.Any) -> str | None:
    return repr(o) if o is not None else None
