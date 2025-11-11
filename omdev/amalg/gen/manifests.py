import ast

from omlish import check

from ...py.tokens import all as tks


##


def is_manifest_comment(line: tks.Tokens) -> bool:
    if not line:
        return False

    return (
        (ft := line[0]).name == 'COMMENT' and
        ft.src.startswith('# @omlish-manifest')
    )


def comment_out_manifest_comment(
        line: tks.Tokens,
        cls: list[tks.Tokens],
        i: int,
) -> tuple[list[tks.Tokens], int]:
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

    out: list[tks.Tokens] = [
        [tks.Token('COMMENT', '# ' + tks.join_toks(ml))]
        for ml in mls
    ]

    return out, i
