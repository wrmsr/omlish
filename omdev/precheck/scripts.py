import dataclasses as dc
import os
import stat
import typing as ta

from .. import magic
from ..py import findimports
from .base import Precheck
from .base import PrecheckContext


##


class ScriptDepsPrecheck(Precheck['ScriptDepsPrecheck.Config']):
    @dc.dataclass(frozen=True)
    class Config(Precheck.Config):
        pass

    def __init__(
            self,
            context: PrecheckContext,
            config: Config = Config(),
    ) -> None:
        super().__init__(config)

        self._context = context

    async def run(self) -> ta.AsyncGenerator[Precheck.Violation]:
        for fp in sorted(magic.find_magic_files(
                magic.PY_MAGIC_STYLE,
                self._context.src_roots,
                keys=['@omlish-script'],
        )):
            if not (stat.S_IXUSR & os.stat(fp).st_mode):
                yield Precheck.Violation(self, f'script {fp} is not executable')

            with open(fp) as f:  # noqa  # FIXME
                src = f.read()

            if not src.startswith('#!/usr/bin/env python3\n'):
                yield Precheck.Violation(self, f'script {fp} lacks correct shebang')

            deps: set[str] = set()

            imp_finder = findimports.ImportFinder()
            for imp in imp_finder.yield_file_imports(fp):
                # FIXME: lame
                if imp.line and 'noqa' in [p.strip() for p in imp.line.split('#')]:
                    continue

                if (imp_tgts := imp_finder.get_import_node_targets(imp.node)) is None:
                    continue

                imp_deps = imp_finder.get_import_deps(imp_tgts)
                deps.update(imp_deps)

            if deps:
                yield Precheck.Violation(self, f'script {fp} has deps: {deps}')
