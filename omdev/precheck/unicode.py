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

        DEFAULT_FILE_EXTENSIONS: ta.ClassVar[ta.AbstractSet[str]] = frozenset([
            'py',

            'c',
            'cc',
            'cu',
            'h',
            'hh',
        ])

        file_extensions: ta.AbstractSet[str] = DEFAULT_FILE_EXTENSIONS

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

    async def _run_file(self, file: str, src: str | None = None) -> ta.AsyncGenerator[Precheck.Violation]:
        if src is None:
            src = self._text_file_cache.get_entry(file).text()

        illegal_chars = {
            ch
            for ch in src
            if ord(ch) > 255
            and unicodedata.category(ch) not in self._config.permitted_categories
        }

        if illegal_chars:
            sl = [
                f'({ch!r}, {unicodedata.category(ch)})'
                for ch in sorted(illegal_chars)
            ]
            yield Precheck.Violation(self, f'source file {file} has illegal unicode characters: {", ".join(sl)}')

    async def _run_py_file(self, py_file: str) -> ta.AsyncGenerator[Precheck.Violation]:
        if isinstance(header_lines := self._headers_cache.get_file_headers(py_file), Exception):
            return
        if any(hl.src.strip() == '# @omlish-precheck-allow-any-unicode' for hl in header_lines):
            return

        async for v in self._run_file(py_file):
            yield v

    async def run(self) -> ta.AsyncGenerator[Precheck.Violation]:
        files = [
            os.path.join(e.root, f)
            for src_root in self._context.src_roots
            for e in self._dir_walk_cache.list_dir(src_root)
            for f in e.files
            if '.' in f
            and any(f.endswith('.' + ext) for ext in self._config.file_extensions)
        ]

        for file in sorted(files):
            if file.endswith('.py'):
                async for v in self._run_py_file(file):
                    yield v

            else:
                async for v in self._run_file(file):
                    yield v
