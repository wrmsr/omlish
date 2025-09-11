import itertools
import typing as ta

from .tokenizert import Token


Tokens: ta.TypeAlias = ta.Sequence[Token]
TokensIterable: ta.TypeAlias = ta.Iterable[Token]


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
        drop_nl: bool = False,
        keep: ta.Container[str] = (),
) -> ta.Iterable[Token]:
    if isinstance(keep, str):
        raise TypeError(keep)
    return (
        t
        for t in toks
        if t.name in keep or (t.name not in WS_NAMES and not (drop_nl and t.name == 'NL'))
    )


def ignore_ws_(
        toks: ta.Iterable[Token],
        *,
        keep: ta.Container[str] = (),
) -> list[Token]:
    return list(ignore_ws(
        toks,
        keep=keep,
    ))


##


def split_lines(ts: TokensIterable) -> list[Tokens]:
    return [list(it) for g, it in itertools.groupby(ts, lambda t: t.line)]


def split_lines_dense(ts: TokensIterable) -> list[Tokens]:
    lines: list[list[Token]] = []
    for t in ts:
        while len(lines) < (t.line or 0):
            lines.append([])
        lines[-1].append(t)
    return lines  # type: ignore[return-value]


def join_toks(ts: TokensIterable) -> str:
    return ''.join(t.src for t in ts)


def join_lines(ls: ta.Iterable[Tokens]) -> str:
    return ''.join(map(join_toks, ls))


##


def match_toks(
        ts: TokensIterable,
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
