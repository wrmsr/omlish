# hi
"""
docstring

hi
"""  # foo
# more
import ast
import typing as ta

from omdev.tokens import all as tks
from omlish.lite.check import check


##


class PyHeaderLine(ta.NamedTuple):
    kind: ta.Literal['comment', 'string']
    s: str
    line: int
    col: int


def get_py_header_lines(src: str) -> list[PyHeaderLine]:
    ret: list[PyHeaderLine] = []

    src_toks = tks.src_to_tokens(src)
    hdr_toks = (
        tok
        for tok in src_toks
        if tok.name == 'COMMENT' or
        (tok.name not in tks.WS_NAMES and tok.name != 'NL')
    )

    for tok in hdr_toks:
        if tok.name == 'COMMENT':
            cs = tok.src.lstrip()
            check.state(cs.startswith('#'))
            cs = cs[1:].lstrip()
            ret.append(PyHeaderLine(
                'comment',
                cs,
                tok.line,
                tok.utf8_byte_offset,
            ))

        elif tok.name == 'STRING':
            ss = ast.literal_eval(tok.src)
            ret.append(PyHeaderLine(
                'string',
                ss,
                tok.line,
                tok.utf8_byte_offset,
            ))

        else:
            break

    return ret


##


def _main() -> None:
    with open(__file__) as f:
        src = f.read()

    hls = get_py_header_lines(src)
    print(hls)


if __name__ == '__main__':
    _main()
