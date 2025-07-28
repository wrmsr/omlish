import dataclasses as dc
import os
import typing as ta
import unicodedata

from omlish.text.filecache import TextFileCache

from .base import Precheck
from .base import PrecheckContext
from .caches import DirWalkCache
from .caches import HeadersCache


##


class UnicodePrecheck(Precheck['UnicodePrecheck.Config']):
    @dc.dataclass(frozen=True)
    class Config(Precheck.Config):
        DEFAULT_PERMITTED_CATEGORIES: ta.ClassVar[ta.AbstractSet[str]] = frozenset([
            'Lu',  # Letter, uppercase
            'Ll',  # Letter, lowercase
            'Lt',  # Letter, titlecase
            'Sm',  # Symbol, math
            'Sc',  # Symbol, currency
            'Sk',  # Symbol, modifier
            'So',  # Symbol, other
        ])

        permitted_categories: ta.AbstractSet[str] = DEFAULT_PERMITTED_CATEGORIES

    def __init__(
            self,
            context: PrecheckContext,
            config: Config = Config(),
            *,
            dir_walk_cache: DirWalkCache,
            text_file_cache: TextFileCache,
            headers_cache: HeadersCache,
    ) -> None:
        super().__init__(config)

        self._context = context

        self._dir_walk_cache = dir_walk_cache
        self._text_file_cache = text_file_cache
        self._headers_cache = headers_cache

    async def _run_py_file(self, py_file: str) -> ta.AsyncGenerator[Precheck.Violation]:
        if isinstance(header_lines := self._headers_cache.get_file_headers(py_file), Exception):
            return
        if any(hl.src.strip() == '# @omlish-precheck-allow-any-unicode' for hl in header_lines):
            return

        src = self._text_file_cache.get_entry(py_file).text()

        illegal_chars = {
            ch
            for ch in src
            if ord(ch) > 255 and
            unicodedata.category(ch) not in self._config.permitted_categories
        }

        if illegal_chars:
            sl = [
                f'({ch!r}, {unicodedata.category(ch)})'
                for ch in sorted(illegal_chars)
            ]
            yield Precheck.Violation(self, f'source file {py_file} has illegal unicode characters: {", ".join(sl)}')

    async def run(self) -> ta.AsyncGenerator[Precheck.Violation]:
        py_files = [
            os.path.join(e.root, f)
            for src_root in self._context.src_roots
            for e in self._dir_walk_cache.list_dir(src_root)
            for f in e.files
            if f.endswith('.py')
        ]
        for py_file in sorted(py_files):
            async for v in self._run_py_file(py_file):
                yield v
