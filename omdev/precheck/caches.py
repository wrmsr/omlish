import ast
import os
import typing as ta

from omlish import dataclasses as dc
from omlish import lang
from omlish.text.filecache import TextFileCache

from ..py.srcheaders import PyHeaderLine
from ..py.srcheaders import get_py_header_lines
from ..py.tokens import all as tks


##


class DirWalkCache:
    @dc.dataclass(frozen=True)
    class Entry:
        root: str
        dirs: ta.Sequence[str]
        files: ta.Sequence[str]

    @lang.cached_function
    def list_dir(self, path: str) -> ta.Sequence[Entry]:
        return [
            self.Entry(root, list(dirs), list(files))
            for root, dirs, files in os.walk(path)
        ]


##


@dc.dataclass(frozen=True)
class AstCache:
    _tfc: TextFileCache = dc.field(repr=False)

    @lang.cached_function
    def get_file_ast(self, path: str) -> ast.AST | Exception:
        try:
            tfe = self._tfc.get_entry(path)
            return ast.parse(tfe.text(), path)
        except Exception as e:  # noqa
            return e


##


@dc.dataclass(frozen=True)
class TokensCache:
    _tfc: TextFileCache = dc.field(repr=False)

    @lang.cached_function
    def get_file_tokens(self, path: str) -> tks.Tokens | Exception:
        try:
            tfe = self._tfc.get_entry(path)
            return tks.src_to_tokens(tfe.text())
        except Exception as e:  # noqa
            return e


##


@dc.dataclass(frozen=True)
class HeadersCache:
    _tfc: TextFileCache = dc.field(repr=False)

    @lang.cached_function
    def get_file_headers(self, path: str) -> ta.Sequence[PyHeaderLine] | Exception:
        try:
            tfe = self._tfc.get_entry(path)
            return get_py_header_lines(tfe.text())
        except Exception as e:  # noqa
            return e
