import dataclasses as dc
import os
import stat
import typing as ta

from omdev import findimports
from omdev import findmagic

from .base import Precheck
from .base import PrecheckContext


##


class ScriptDepsPrecheck(Precheck['ScriptDepsPrecheck.Config']):
    @dc.dataclass(frozen=True)
    class Config(Precheck.Config):
        pass

    def __init__(self, context: PrecheckContext, config: Config = Config()) -> None:
        super().__init__(context, config)

    async def run(self) -> ta.AsyncGenerator[Precheck.Violation, None]:
        for fp in findmagic.find_magic(
                self._context.src_roots,
                ['# @omlish-script'],
                ['py'],
        ):
            if not (stat.S_IXUSR & os.stat(fp).st_mode):
                yield Precheck.Violation(self, f'script {fp} is not executable')

            with open(fp) as f:  # noqa  # FIXME
                src = f.read()

            if not src.startswith('#!/usr/bin/env python3\n'):
                yield Precheck.Violation(self, f'script {fp} lacks correct shebang')

            imps = findimports.find_imports(fp)
            deps = findimports.get_import_deps(imps)
            if deps:
                yield Precheck.Violation(self, f'script {fp} has deps: {deps}')
