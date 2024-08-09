"""
Conventions:
 - must import whole global modules, if aliased must all match
 - must import 'from' items for local modules

TODO:
 - check 3.8 compat
 - scan: `#@ ominfra-amalg`
 - make gen
 - argparse
 - more sanity checks lol
 - flake8 / ruff mgmt
 - if shebang chmod a+x

Targets:
 - interp
 - pyproject
 - precheck
 - build
 - pyremote
 - bootstrap
 - deploy
 - supervisor?
"""
import dataclasses as dc
import io
import itertools
import os.path
import typing as ta

import tokenize_rt as trt

from omlish import check
from omlish import collections as col


Tokens: ta.TypeAlias = ta.Sequence[trt.Token]


##


WS_NAMES = ('UNIMPORTANT_WS', 'NEWLINE', 'COMMENT')


def is_ws(tok: trt.Token) -> bool:
    return tok.name in WS_NAMES


def ignore_ws(toks: ta.Iterable[trt.Token]) -> ta.Iterable[trt.Token]:
    return (t for t in toks if not is_ws(t))


HEADER_NAMES = (*WS_NAMES, 'COMMENT', 'STRING')


def split_header_lines(lines: ta.Iterable[Tokens]) -> tuple[list[Tokens], list[Tokens]]:
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


def join_toks(ts: Tokens) -> str:
    return ''.join(t.src for t in ts)


def join_lines(ls: ta.Iterable[Tokens]) -> str:
    return ''.join(map(join_toks, ls))


##


@dc.dataclass(frozen=True, kw_only=True)
class Import:
    mod: str
    item: str | None
    as_: str | None

    src_path: str
    line: int

    mod_path: str | None

    toks: Tokens = dc.field(repr=False)


def make_import(
        lts: Tokens,
        *,
        src_path: str,
        mounts: ta.Mapping[str, str],
) -> Import | None:
    if not lts:
        return None
    ft = lts[0]

    if ft.name != 'NAME' or ft.src not in ('import', 'from'):
        return None

    ml = []
    il: list[str] | None = None
    as_ = None
    for tok in (it := iter(ignore_ws(lts[1:]))):
        if tok.name in ('NAME', 'OP'):
            if tok.src == 'as':
                check.none(as_)
                nt = next(it)
                check.equal(nt.name, 'NAME')
                as_ = nt.src
            elif tok.src == 'import':
                check.equal(ft.src, 'from')
                il = []
            elif il is not None:
                il.append(tok.src)
            else:
                ml.append(tok.src)
        else:
            raise Exception(tok)

    mod = ''.join(ml)
    item = ''.join(il) if il is not None else None

    if (mnt := mounts.get(mod.partition('.')[0])) is not None:
        ps = mod.split('.')
        mod_path = os.path.abspath(os.path.join(
            mnt,
            *ps[1:-1],
            ps[-1] + '.py',
        ))

    elif not mod.startswith('.'):
        mod_path = None

    else:
        parts = mod.split('.')
        nd = len(parts) - parts[::-1].index('')
        mod_path = os.path.abspath(os.path.join(
            os.path.dirname(src_path),
            '../' * (nd - 1),
            *parts[nd:-1],
            parts[-1] + '.py',
        ))

        mod = check.isinstance(mod_path, str)

    return Import(
        mod=mod,
        item=item,
        as_=as_,

        src_path=src_path,
        line=ft.line,

        mod_path=mod_path,

        toks=lts,
    )


##


@dc.dataclass(frozen=True, kw_only=True)
class Typing:
    src: str

    src_path: str
    line: int

    toks: Tokens = dc.field(repr=False)


def make_typing(
        lts: Tokens,
        *,
        src_path: str,
) -> Typing | None:
    if not lts or lts[0].name == 'UNIMPORTANT_WS':
        return None

    wts = list(ignore_ws(lts))
    if not (
            len(wts) >= 5 and
            wts[0].name == 'NAME' and
            wts[1].name == 'OP' and wts[1].src == '=' and
            wts[2].name == 'NAME' and wts[2].src == 'ta' and
            wts[3].name == 'OP' and wts[3].src == '.'

    ):
        return None

    return Typing(
        src=join_toks(lts),

        src_path=src_path,
        line=wts[0].line,

        toks=lts,
    )


##


@dc.dataclass(frozen=True, kw_only=True)
class SrcFile:
    path: str

    src: str = dc.field(repr=False)
    tokens: Tokens = dc.field(repr=False)
    lines: ta.Sequence[Tokens] = dc.field(repr=False)

    header_lines: ta.Sequence[Tokens] = dc.field(repr=False)
    imports: ta.Sequence[Import] = dc.field(repr=False)
    typings: ta.Sequence[Typing] = dc.field(repr=False)
    content_lines: ta.Sequence[Tokens] = dc.field(repr=False)


def make_src_file(
        path: str,
        *,
        mounts: ta.Mapping[str, str],
) -> SrcFile:
    with open(path) as f:
        src = f.read().strip()

    tokens = trt.src_to_tokens(src)
    lines = [list(it) for g, it in itertools.groupby(tokens, lambda t: t.line)]

    hls, cls = split_header_lines(lines)

    imps: list[Import] = []
    tys: list[Typing] = []
    ctls: list[Tokens] = []

    for line in cls:
        if (imp := make_import(
                line,
                src_path=path,
                mounts=mounts,
        )) is not None:
            imps.append(imp)

        elif (ty := make_typing(
                line,
                src_path=path,
        )) is not None:
            tys.append(ty)

        else:
            ctls.append(line)

    return SrcFile(
        path=path,

        src=src,
        tokens=tokens,
        lines=lines,

        header_lines=hls,
        imports=imps,
        typings=tys,
        content_lines=ctls,
    )


##


SECTION_SEP = '#' * 40 + '\n'

RUFF_DISABLES: ta.Sequence[str] = [
    # 'UP006',  # Use `list` instead of `ta.List` for type annotation
    # 'UP007',  # Use `X | Y` for type annotations
]


def gen_amalg(
        main_path: str,
        *,
        mounts: ta.Mapping[str, str],
) -> str:
    src_files: dict[str, SrcFile] = {}
    todo = [main_path]
    while todo:
        src_path = todo.pop()
        if src_path in src_files:
            continue

        f = make_src_file(
            src_path,
            mounts=mounts,
        )
        src_files[src_path] = f

        for imp in f.imports:
            if (mp := imp.mod_path) is not None:
                todo.append(mp)

    ##

    out = io.StringIO()

    ##

    mf = src_files[main_path]
    if mf.header_lines:
        out.write(join_lines(mf.header_lines))

    if RUFF_DISABLES:
        out.write(f'# ruff: noqa: {" ".join(RUFF_DISABLES)}\n')

    ##

    all_imps = [i for f in src_files.values() for i in f.imports]
    gl_imps = [i for i in all_imps if i.mod_path is None]

    dct: dict = {}
    for imp in gl_imps:
        dct.setdefault((imp.mod, imp.item, imp.as_), []).append(imp)
    for _, l in sorted(dct.items()):
        out.write(join_toks(l[0].toks))
    if dct:
        out.write('\n\n')

    ##

    ts = list(col.toposort({  # noqa
        f.path: {mp for i in f.imports if (mp := i.mod_path) is not None}
        for f in src_files.values()
    }))
    sfs = [sf for ss in ts for sf in sorted(ss)]

    ##

    tys = set()
    for sf in sfs:
        f = src_files[sf]
        for ty in f.typings:
            if ty.src not in tys:
                out.write(ty.src)
                tys.add(ty.src)
    if tys:
        out.write('\n\n')

    ##

    for i, sf in enumerate(sfs):
        f = src_files[sf]
        out.write(SECTION_SEP)
        if f is not mf:
            rp = os.path.relpath(f.path, mf.path)
        else:
            rp = os.path.basename(f.path)
        out.write(f'# {rp}\n')
        if f is not mf and f.header_lines:
            out.write(join_lines(f.header_lines))
        out.write(f'\n\n')
        sf_src = join_lines(f.content_lines)
        out.write(sf_src.strip())
        if i < len(sfs) - 1:
            out.write('\n\n\n')
        else:
            out.write('\n')

    ##

    return out.getvalue()


##


def _main() -> None:
    pass


if __name__ == '__main__':
    _main()
