import itertools
import typing as ta

from .tokenizert import Token


Tokens: ta.TypeAlias = ta.Sequence[Token]


##


WS_NAMES = (
    'UNIMPORTANT_WS',
    'NEWLINE',
    'COMMENT',
    'INDENT',
    'DEDENT',
)


def is_ws(tok: Token) -> bool:
    return tok.name in WS_NAMES


def ignore_ws(
        toks: ta.Iterable[Token],
        *,
        keep: ta.Container[str] = (),
) -> ta.Iterable[Token]:
    return (
        t
        for t in toks
        if t.name in keep or t.name not in WS_NAMES
    )


##


def split_lines(ts: Tokens) -> list[Tokens]:
    return [list(it) for g, it in itertools.groupby(ts, lambda t: t.line)]


def join_toks(ts: Tokens) -> str:
    return ''.join(t.src for t in ts)


def join_lines(ls: ta.Iterable[Tokens]) -> str:
    return ''.join(map(join_toks, ls))


##


def match_toks(
        ts: ta.Iterable[Token],
        pat: ta.Sequence[tuple[str | None, str | tuple[str, ...] | None]],
) -> bool:
    it = iter(ts)
    for pn, ps in pat:
        try:
            t = next(it)
        except StopIteration:
            return False
        if pn is not None and t.name != pn:
            return False
        if ps is not None:
            if isinstance(ps, str):
                if t.src != ps:
                    return False
            elif isinstance(ps, tuple):
                if t.src not in ps:
                    return False
            else:
                raise TypeError(ps)
    return True
