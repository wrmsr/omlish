import ast
import dataclasses as dc
import os.path
import typing as ta

from omlish.text.filecache import TextFileCache

from .base import Precheck
from .base import PrecheckContext
from .caches import AstCache
from .caches import DirWalkCache
from .caches import HeadersCache


##


class RootRelativeImportPrecheck(Precheck['RootRelativeImportPrecheck.Config']):
    @dc.dataclass(frozen=True)
    class Config(Precheck.Config):
        pass

    def __init__(
            self,
            context: PrecheckContext,
            config: Config = Config(),
            *,
            dir_walk_cache: DirWalkCache,
            headers_cache: HeadersCache,
            ast_cache: AstCache,
            text_file_cache: TextFileCache,
    ) -> None:
        super().__init__(config)

        self._context = context

        self._dir_walk_cache = dir_walk_cache
        self._headers_cache = headers_cache
        self._ast_cache = ast_cache
        self._text_file_cache = text_file_cache

    async def _run_py_file(self, py_file: str, src_root: str) -> ta.AsyncGenerator[Precheck.Violation]:
        if isinstance(header_lines := self._headers_cache.get_file_headers(py_file), Exception):
            return
        if any(hl.src.strip() == '# ruff: noqa' for hl in header_lines):
            return

        py_file_lines = self._text_file_cache.get_entry(py_file).lines()

        py_file_ast = self._ast_cache.get_file_ast(py_file)
        if not isinstance(py_file_ast, ast.Module):
            return

        for cur_node in ast.walk(py_file_ast):
            if not isinstance(cur_node, (ast.Import, ast.ImportFrom)):
                continue

            # FIXME: lame lol
            if py_file_lines[cur_node.lineno - 1].strip().endswith('# noqa'):
                continue

            if isinstance(cur_node, ast.Import):
                imp_alias: ast.alias
                for imp_alias in cur_node.names:
                    if imp_alias.name.split('.')[0] == src_root:
                        yield Precheck.Violation(self, f'Root relative import in file {py_file}: {imp_alias.name!r}')

            elif isinstance(cur_node, ast.ImportFrom):
                if cur_node.level == 0 and cur_node.module and cur_node.module.split('.')[0] == src_root:
                    yield Precheck.Violation(self, f'Root relative import in file {py_file}: {cur_node.module!r}')

        return

    async def _run_src_root(self, src_root: str) -> ta.AsyncGenerator[Precheck.Violation]:
        py_files = [
            os.path.join(e.root, f)
            for e in self._dir_walk_cache.list_dir(src_root)
            for f in e.files
            if f.endswith('.py')
        ]

        for py_file in sorted(py_files):
            async for v in self._run_py_file(py_file, src_root):
                yield v

    async def run(self) -> ta.AsyncGenerator[Precheck.Violation]:
        for src_root in sorted(self._context.src_roots):
            async for v in self._run_src_root(src_root):
                yield v
