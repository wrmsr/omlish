"""
Conventions:
 - must import whole global modules, if aliased must all match
 - must import 'from' items for local modules

TODO:
 - !! check only importing lite code
 - !! strip manifests? or relegate them to a separate tiny module ala __main__.py?
  - # @omlish-no-amalg ? in cli.types? will strip stmt (more than 1 line) following @manifest, so shouldn't import
 - more sanity checks lol
 - typealias - support # noqa, other comments, and lamely support multiline by just stealing lines till it parses
 - remove `if __name__ == '__main__':` blocks - thus, convention: no def _main() for these

See:
 - https://github.com/xonsh/amalgamate - mine is for portability not speed, and doesn't try to work on unmodified code

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
import argparse
import dataclasses as dc
import io
import logging
import os.path
import textwrap
import typing as ta

import tokenize_rt as trt

from omlish import check
from omlish import collections as col
from omlish import lang
from omlish.lite.runtime import LITE_REQUIRED_PYTHON_VERSION
from omlish.logs import all as logs

from .. import tokens as tks
from .imports import Import
from .imports import make_import
from .manifests import comment_out_manifest_comment
from .manifests import is_manifest_comment
from .resources import build_resource_lines
from .resources import is_root_level_resources_read
from .strip import split_header_lines
from .strip import strip_header_lines
from .strip import strip_main_lines
from .types import Tokens
from .typing import Typing
from .typing import is_root_level_if_type_checking_block
from .typing import make_typing
from .typing import skip_root_level_if_type_checking_block


log = logging.getLogger(__name__)


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

    ruff_noqa: ta.AbstractSet[str] = dc.field(repr=False)

    has_binary_resources: bool = False


def make_src_file(
        path: str,
        *,
        mounts: ta.Mapping[str, str],
) -> SrcFile:
    with open(path) as f:
        src = f.read().strip()

    tokens = trt.src_to_tokens(src)
    lines = tks.split_lines(tokens)

    hls, cls = split_header_lines(lines)

    hls = strip_header_lines(hls)
    rnls, hls = col.partition(hls, lambda l: tks.join_toks(l).startswith('# ruff: noqa: '))

    imps: list[Import] = []
    tys: list[Typing] = []
    ctls: list[Tokens] = []

    has_binary_resources = False

    i = 0
    while i < len(cls):
        line = cls[i]
        i += 1

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

        elif is_manifest_comment(line):
            out, i = comment_out_manifest_comment(line, cls, i)
            ctls.extend(out)

        elif is_root_level_if_type_checking_block(line):
            i = skip_root_level_if_type_checking_block(cls, i)

        elif (rsrc := is_root_level_resources_read(line)) is not None:
            ctls.extend(build_resource_lines(
                rsrc,
                path,
            ))

            if rsrc.kind == 'binary':
                has_binary_resources = True

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

        ruff_noqa=set(lang.flatten(tks.join_toks(l).strip().split()[3:] for l in rnls)),  # noqa

        has_binary_resources=has_binary_resources,
    )


##


SECTION_SEP = '#' * 40 + '\n'

RUFF_DISABLES: ta.AbstractSet[str] = {
    'UP006',  # non-pep585-annotation
    'UP007',  # non-pep604-annotation
    'UP036',  # outdated-version-block
}

OUTPUT_COMMENT = '# @omlish-amalg-output '
SCAN_COMMENT = '# @omlish-amalg '


def gen_amalg(
        main_path: str,
        *,
        mounts: ta.Mapping[str, str],
        output_dir: str | None = None,
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

    hls = []

    mf = src_files[main_path]
    if mf.header_lines:
        hls.extend([
            hl
            for hlts in mf.header_lines
            if not (hl := tks.join_toks(hlts)).startswith(SCAN_COMMENT)
        ])

    if output_dir is not None:
        ogf = os.path.relpath(main_path, output_dir)
    else:
        ogf = os.path.basename(main_path)

    nhls = []
    nhls.extend([
        '#!/usr/bin/env python3\n',
        '# noinspection DuplicatedCode\n',
        '# @omlish-lite\n',
        '# @omlish-script\n',
        f'{OUTPUT_COMMENT.strip()} {ogf}\n',
    ])

    ruff_disables = sorted({
        *lang.flatten(f.ruff_noqa for f in src_files.values()),
        *RUFF_DISABLES,
    })
    if ruff_disables:
        nhls.append(f'# ruff: noqa: {" ".join(sorted(ruff_disables))}\n')

    hls = [*nhls, *hls]
    out.write(''.join(hls))

    ##

    all_imps = [i for f in src_files.values() for i in f.imports]
    gl_imps = [i for i in all_imps if i.mod_path is None]

    dct: dict = {
        ('sys', None, None): ['import sys\n'],
    }
    if any(sf.has_binary_resources for sf in src_files.values()):
        dct[('base64', None, None)] = ['import base64\n']
    for imp in gl_imps:
        dct.setdefault((imp.mod, imp.item, imp.as_), []).append(imp)
    for _, l in sorted(dct.items()):
        il = l[0]
        out.write(il if isinstance(il, str) else tks.join_toks(il.toks))
    if dct:
        out.write('\n\n')

    ##

    out.write(SECTION_SEP)
    out.write('\n\n')

    version_check_fail_msg = (
        f'Requires python {LITE_REQUIRED_PYTHON_VERSION!r}, '
        f'got {{sys.version_info}} from {{sys.executable}}'
    )
    out.write(textwrap.dedent(f"""
    if sys.version_info < {LITE_REQUIRED_PYTHON_VERSION!r}:
        raise OSError(f{version_check_fail_msg!r})  # noqa
    """).lstrip())
    out.write('\n\n')

    ##

    ts = list(col.toposort({  # noqa
        f.path: {mp for i in f.imports if (mp := i.mod_path) is not None}
        for f in src_files.values()
    }))
    sfs = [sf for ss in ts for sf in sorted(ss)]

    ##

    tyd: dict[str, list[Typing]] = {}
    tys = set()
    for sf in sfs:
        f = src_files[sf]
        for ty in f.typings:
            if ty.src not in tys:
                tyd.setdefault(f.path, []).append(ty)
                tys.add(ty.src)
    if tys:
        out.write(SECTION_SEP)
        out.write('\n\n')
    for i, (sf, ftys) in enumerate(tyd.items()):
        f = src_files[sf]
        if i:
            out.write('\n')
        if f is not mf:
            rp = os.path.relpath(f.path, os.path.dirname(mf.path))
        else:
            rp = os.path.basename(f.path)
        out.write(f'# {rp}\n')
        for ty in ftys:
            out.write(ty.src)
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
            out.write(tks.join_lines(f.header_lines))
        out.write(f'\n\n')
        cls = f.content_lines
        if f is not mf:
            cls = strip_main_lines(cls)
        sf_src = tks.join_lines(cls)
        out.write(sf_src.strip())
        if i < len(sfs) - 1:
            out.write('\n\n\n')
        else:
            out.write('\n')

    ##

    return out.getvalue()


##


def _gen_one(
        input_path: str,
        output_path: str | None,
        *,
        mounts: ta.Mapping[str, str],
) -> None:
    log.info('Generating: %s -> %s', input_path, output_path)

    src = gen_amalg(
        input_path,
        mounts=mounts,
        output_dir=os.path.dirname(output_path if output_path is not None else input_path),
    )

    if output_path is not None:
        with open(output_path, 'w') as f:
            f.write(src)
        os.chmod(output_path, os.stat(input_path).st_mode)

    else:
        print(src)


def _scan_one(
        input_path: str,
        **kwargs: ta.Any,
) -> None:
    if not input_path.endswith('.py'):
        return

    with open(input_path) as f:
        src = f.read()

    sls = [l for l in src.splitlines() if l.startswith(SCAN_COMMENT)]
    for sl in sls:
        sas = sl[len(SCAN_COMMENT):].split()
        if len(sas) != 1:
            raise Exception(f'Invalid scan args: {input_path=} {sas=}')

        output_path = os.path.abspath(os.path.join(os.path.dirname(input_path), sas[0]))
        _gen_one(
            input_path,
            output_path,
            **kwargs,
        )


def _gen_cmd(args) -> None:
    if not os.path.isfile('pyproject.toml'):
        raise Exception('Not in project root')

    mounts = {}
    for m in args.mounts or ():
        if ':' not in m:
            mounts[m] = os.path.abspath(m)
        else:
            k, v = m.split(':')
            mounts[k] = os.path.abspath(v)

    for i in args.inputs:
        if os.path.isdir(i):
            log.info('Scanning %s', i)
            for we_dirpath, we_dirnames, we_filenames in os.walk(i):  # noqa
                for fname in we_filenames:
                    _scan_one(
                        os.path.abspath(os.path.join(we_dirpath, fname)),
                        mounts=mounts,
                    )

        else:
            output_dir = args.output
            if output_dir is not None:
                output_path = check.isinstance(os.path.join(output_dir, os.path.basename(i)), str)
            else:
                output_path = None

            _gen_one(
                os.path.abspath(i),
                output_path,
                mounts=mounts,
            )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers()

    parser_gen = subparsers.add_parser('gen')
    parser_gen.add_argument('--mount', '-m', dest='mounts', action='append')
    parser_gen.add_argument('--output', '-o')
    parser_gen.add_argument('inputs', nargs='+')
    parser_gen.set_defaults(func=_gen_cmd)

    return parser


def _main() -> None:
    logs.configure_standard_logging('INFO')

    parser = _build_parser()
    args = parser.parse_args()
    if not getattr(args, 'func', None):
        parser.print_help()
    else:
        args.func(args)


if __name__ == '__main__':
    _main()
