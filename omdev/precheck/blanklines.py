import dataclasses as dc
import os
import typing as ta

from omlish.text.filecache import TextFileCache

from .base import Precheck
from .base import PrecheckContext
from .caches import DirWalkCache
from .caches import HeadersCache


##


class BlankLinesPrecheck(Precheck['BlankLinesPrecheck.Config']):
    @dc.dataclass(frozen=True)
    class Config(Precheck.Config):
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

    async def _run_file(self, file: str) -> ta.AsyncGenerator[Precheck.Violation]:
        src = self._text_file_cache.get_entry(file).text()

        if src and not src.splitlines()[0]:
            yield Precheck.Violation(self, f'source file {file} starts with blank line')

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
            async for v in self._run_file(file):
                yield v
