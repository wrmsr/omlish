import ast
import dataclasses as dc
import typing as ta

from omlish.lite.check import check

from .tokens import all as tks


##


@dc.dataclass(frozen=True)
class PyHeaderLine:
    kind: ta.Literal['comment', 'string']
    src: str
    content: str
    line: int
    col: int


def get_py_header_lines(src: str) -> list[PyHeaderLine]:
    ret: list[PyHeaderLine] = []

    src_toks = tks.iter_src_to_tokens(src)
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
                kind='comment',
                src=tok.src,
                content=cs,
                line=check.isinstance(tok.line, int),
                col=check.isinstance(tok.utf8_byte_offset, int),
            ))

        elif tok.name == 'STRING':
            ss = ast.literal_eval(tok.src)
            ret.append(PyHeaderLine(
                kind='string',
                src=tok.src,
                content=ss,
                line=check.isinstance(tok.line, int),
                col=check.isinstance(tok.utf8_byte_offset, int),
            ))

        else:
            break

    return ret


##


# @omlish-manifest
_CLI_MODULE = {'!.cli.types.CliModule': {
    'name': 'py/srcheaders',
    'module': __name__,
}}


if __name__ == '__main__':
    def _main() -> None:
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument('file')
        args = parser.parse_args()

        #

        with open(args.file) as f:
            src = f.read()

        #

        hls = get_py_header_lines(src)

        #

        import json

        print(json.dumps(
            [dc.asdict(hl) for hl in hls],
            indent=2,
        ))

    _main()
