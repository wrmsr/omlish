# @omlish-lite
import shlex


def shlex_needs_quote(s: str) -> bool:
    return bool(s) and len(list(shlex.shlex(s))) > 1


def shlex_maybe_quote(s: str) -> str:
    if shlex_needs_quote(s):
        return shlex.quote(s)
    else:
        return s
