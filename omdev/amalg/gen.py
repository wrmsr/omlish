import io
import os.path
import textwrap
import typing as ta

from omlish import cached
from omlish import lang
from omlish.algorithm import all as alg
from omlish.lite.runtime import LITE_REQUIRED_PYTHON_VERSION

from ..git.magic import GIT_DIFF_OMIT_MAGIC
from ..tokens import all as tks
from .srcfiles import SrcFile
from .srcfiles import make_src_file
from .strip import strip_main_lines
from .typing import Typing


##


SECTION_SEP = '#' * 40 + '\n'

RUFF_DISABLES: ta.AbstractSet[str] = {
    'UP006',  # non-pep585-annotation
    'UP007',  # non-pep604-annotation
    'UP036',  # outdated-version-block
}

OUTPUT_COMMENT = '# @omlish-amalg-output '
SCAN_COMMENT = '# @omlish-amalg '


class AmalgGenerator:
    def __init__(
            self,
            main_path: str,
            *,
            mounts: ta.Mapping[str, str],
            output_dir: str | None = None,
    ) -> None:
        super().__init__()

        self._main_path = main_path
        self._mounts = mounts
        self._output_dir = output_dir

    @cached.function
    def _src_files(self) -> dict[str, SrcFile]:
        src_files: dict[str, SrcFile] = {}
        todo = [self._main_path]
        while todo:
            src_path = todo.pop()
            if src_path in src_files:
                continue

            f = make_src_file(
                src_path,
                mounts=self._mounts,
            )
            src_files[src_path] = f

            for imp in f.imports:
                if (mp := imp.mod_path) is not None:
                    todo.append(mp)

        return src_files

    @cached.function
    def _main_file(self) -> SrcFile:
        return self._src_files()[self._main_path]

    @cached.function
    def _header_lines(self) -> list[str]:
        header_lines = []

        if self._main_file().header_lines:
            header_lines.extend([
                hl
                for hlts in self._main_file().header_lines
                if not (hl := tks.join_toks(hlts)).startswith(SCAN_COMMENT)
            ])

        if self._output_dir is not None:
            ogf = os.path.relpath(self._main_path, self._output_dir)
        else:
            ogf = os.path.basename(self._main_path)

        additional_header_lines = [
            '#!/usr/bin/env python3\n',
            '# noinspection DuplicatedCode\n',
            '# @omlish-lite\n',
            '# @omlish-script\n',
            '# @omlish-generated\n',
            f'{OUTPUT_COMMENT.strip()} {ogf}\n',
            f'# {GIT_DIFF_OMIT_MAGIC}\n',
        ]

        ruff_disables = sorted({
            *lang.flatten(f.ruff_noqa for f in self._src_files().values()),
            *RUFF_DISABLES,
        })
        if ruff_disables:
            additional_header_lines.append(f'# ruff: noqa: {" ".join(sorted(ruff_disables))}\n')

        return [*additional_header_lines, *header_lines]

    @cached.function
    def gen_amalg(self) -> str:
        src_files = self._src_files()

        ##

        out = io.StringIO()

        ##

        out.write(''.join(self._header_lines()))

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
        for _, l in sorted(
                dct.items(),
                key=lambda t: (t[0][0], t[0][1] or '', t[0][2] or ''),
        ):
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

        ts = list(alg.toposort({  # noqa
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
            if f is not self._main_file():
                rp = os.path.relpath(f.path, os.path.dirname(self._main_file().path))
            else:
                rp = os.path.basename(f.path)
            out.write(f'# {rp}\n')
            for ty in ftys:
                out.write(ty.src)
        if tys:
            out.write('\n\n')

        ##

        main_file = self._main_file()
        for i, sf in enumerate(sfs):
            f = src_files[sf]
            out.write(SECTION_SEP)
            if f is not main_file:
                rp = os.path.relpath(f.path, main_file.path)
            else:
                rp = os.path.basename(f.path)
            out.write(f'# {rp}\n')
            if f is not main_file and f.header_lines:
                out.write(tks.join_lines(f.header_lines))
            out.write(f'\n\n')
            cls = f.content_lines
            if f is not main_file:
                cls = strip_main_lines(cls)
            sf_src = tks.join_lines(cls)
            out.write(sf_src.strip())
            if i < len(sfs) - 1:
                out.write('\n\n\n')
            else:
                out.write('\n')

        ##

        return out.getvalue()
