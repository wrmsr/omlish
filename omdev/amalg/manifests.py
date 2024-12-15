import ast

import tokenize_rt as trt

from omlish import check

from .. import tokens as tks
from .types import Tokens


##


def is_manifest_comment(line: Tokens) -> bool:
    if not line:
        return False

    return (
        (ft := line[0]).name == 'COMMENT' and
        ft.src.startswith('# @omlish-manifest')
    )


def comment_out_manifest_comment(
        line: Tokens,
        cls: list[Tokens],
        i: int,
) -> tuple[list[Tokens], int]:
    mls = [line]
    while True:
        mls.append(cls[i])
        i += 1

        msrc = tks.join_lines(mls).strip()
        try:
            node = ast.parse(msrc)
        except SyntaxError:
            continue

        mmod = check.isinstance(node, ast.Module)
        check.isinstance(check.single(mmod.body), ast.Assign)
        break

    out: list[Tokens] = [
        [trt.Token('COMMENT', '# ' + tks.join_toks(ml))]
        for ml in mls
    ]

    return out, i
