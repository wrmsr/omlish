import re
import typing as ta

from ... import magic
from ...py.tokens import all as tks


##


HEADER_NAMES = (*tks.WS_NAMES, 'COMMENT', 'STRING')


def split_header_lines(lines: ta.Iterable[tks.Tokens]) -> tuple[list[tks.Tokens], list[tks.Tokens]]:
    ws = []
    nws = []
    for line in (it := iter(lines)):
        if line[0].name in HEADER_NAMES:
            ws.append(line)
        else:
            nws.append(line)
            nws.extend(it)
            break
    return ws, nws


##


IF_MAIN_PAT = re.compile(r'if\s+__name__\s+==\s+[\'"]__main__[\'"]\s*:')


def strip_main_lines(cls: ta.Sequence[tks.Tokens]) -> list[tks.Tokens]:
    out = []

    for l in (it := iter(cls)):
        if IF_MAIN_PAT.fullmatch(tks.join_toks(l).strip()):
            for l in it:
                if l[0].name not in ('INDENT', 'UNIMPORTANT_WS') and tks.join_toks(l).strip():
                    break
        else:
            out.append(l)

    return out


##


STRIPPED_HEADER_MAGICS = [
    '@omlish-lite',
    '@omlish-script',
]

STRIPPED_HEADER_PAT = magic.compile_magic_style_pat(
    magic.PY_MAGIC_STYLE,
    keys=STRIPPED_HEADER_MAGICS,
)


def strip_header_lines(hls: ta.Sequence[tks.Tokens]) -> list[tks.Tokens]:
    if hls and tks.join_toks(hls[0]).startswith('#!'):
        hls = hls[1:]
    out = []
    for l in hls:
        ls = tks.join_toks(l)
        if not STRIPPED_HEADER_PAT.fullmatch(ls):
            out.append(l)
    return out
