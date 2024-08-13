import itertools
import typing as ta

from omlish import lang


if ta.TYPE_CHECKING:
    import tokenize_rt as trt
else:
    trt = lang.proxy_import('tokenize_rt')


Tokens: ta.TypeAlias = ta.Sequence['trt.Token']


##


WS_NAMES = ('UNIMPORTANT_WS', 'NEWLINE', 'COMMENT')


def is_ws(tok: 'trt.Token') -> bool:
    return tok.name in WS_NAMES


def ignore_ws(toks: ta.Iterable['trt.Token']) -> ta.Iterable['trt.Token']:
    return (t for t in toks if not is_ws(t))


##


def split_lines(ts: Tokens) -> list[Tokens]:
    return [list(it) for g, it in itertools.groupby(ts, lambda t: t.line)]


def join_toks(ts: Tokens) -> str:
    return ''.join(t.src for t in ts)


def join_lines(ls: ta.Iterable[Tokens]) -> str:
    return ''.join(map(join_toks, ls))
