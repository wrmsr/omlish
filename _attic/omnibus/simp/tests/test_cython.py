"""
TODO:
 - regex first, run through tokenizer next to skip strs (prob have to reconcile w/ regex, tok prob discards cmnts)
 - move all to omnibus.pyasts - + Analysis
 - ** need to disable cy hooks when importing to gen cy hooks lol **
 - *also* support nicer deco's, but comments have to be first-class for circdeps (lang, ...) - this is high in the stack
 - MarkedFileFnResolver -> marked 'object' resolver? move to om.pyasts somehow

cy nodes:
 - DEF
 - cdef var
 - cdef fn
"""
import ast
import bisect
import dataclasses as dc
import glob
import os.path
import types
import typing as ta

import yaml

from .. import rendering as ren
from ... import check
from ... import lang  # noqa
from ... import properties
from ... import pyasts
from ...serde import mapping as sm
from ..pyasts import translate


_HC_PREFIX = '# @simp.'


@dc.dataclass(frozen=True)
class MarkedFn:
    mark: str
    fn: ta.Callable
    pyast: ast.AST
    mod: types.ModuleType


class MarkedFileFnResolver(ta.Iterable[MarkedFn]):
    def __init__(self, file_name: str, mark_prefix: str = _HC_PREFIX) -> None:
        super().__init__()
        self._file_name = file_name
        self._mark_prefix = mark_prefix

    @properties.cached  # noqa
    @property
    def content(self) -> str:
        with open(self._file_name, 'r') as f:
            return f.read()

    @properties.cached  # noqa
    @property
    def mod(self) -> types.ModuleType:
        n, _, ext = self._file_name.rpartition('.')
        check.state(ext == 'py')
        return lang.import_module(n.replace(os.path.sep, '.'))

    @properties.cached
    @property
    def lines(self) -> ta.Sequence[str]:
        return self.content.splitlines()

    @properties.cached  # noqa
    @property
    def marked_linenos(self) -> ta.AbstractSet[int]:
        return {i for i, l in enumerate(self.lines) if l.strip().startswith(self._mark_prefix)}

    @properties.cached  # noqa
    @property
    def pyast(self) -> ast.AST:
        return ast.parse(self.content, 'exec')

    @properties.cached  # noqa
    @property
    def basic(self) -> pyasts.BasicAnalysis:
        return pyasts.analyze(self.pyast)

    @properties.cached  # noqa
    @property
    def first_nodes_by_lineno(self) -> ta.Mapping[int, ast.AST]:
        dct = {}
        for cur in ast.walk(self.pyast):
            if (
                    isinstance(cur, ast.AST) and
                    hasattr(cur, 'lineno') and
                    cur.lineno and
                    cur.lineno not in dct
            ):
                dct[cur.lineno] = cur
        return dct

    @properties.cached  # noqa
    @property
    def marked_pyasts_by_mark_lineno(self) -> ta.Mapping[int, ast.AST]:
        if not self.marked_linenos:
            return {}
        dct = {}
        linenos = sorted(self.first_nodes_by_lineno)
        for ln in self.marked_linenos:
            i = bisect.bisect(linenos, ln)
            # TODO: while(isinstance(hcn, ast.Decorator)): ...
            dct[ln] = self.first_nodes_by_lineno[linenos[i]]
        return dct

    class FnResolver:
        def __init__(self, parent: 'MarkedFileFnResolver', mark_lineno: int) -> None:
            super().__init__()
            self._parent = parent
            self._mark_lineno = mark_lineno

            self._mark = self._parent.lines[self._mark_lineno]
            self._pyast = self._parent.marked_pyasts_by_mark_lineno[mark_lineno]

        @properties.cached  # noqa
        @property
        def mqn(self) -> str:
            ps = []
            c = self._pyast
            while True:
                p = self._parent.basic.parents_by_node[c]
                if not p:
                    break
                ps.append(p)
                c = p

            ns = []
            check.isinstance(ps[-1], ast.Module)
            for p in ps[:-1]:
                if isinstance(p, ast.ClassDef):
                    ns.append(p.name)
                else:
                    raise TypeError(p)

            return '.'.join([*ns, self._pyast.name])

        @properties.cached  # noqa
        @property
        def fn(self) -> ta.Callable:
            o = self._parent.mod
            for p in self.mqn.split('.'):
                o = getattr(o, p)
            return check.callable(o)

        @properties.cached  # noqa
        @property
        def marked_fn(self) -> MarkedFn:
            return MarkedFn(
                mark=self._mark,
                fn=self.fn,
                pyast=self._pyast,
                mod=self._parent.mod,
            )

    def __iter__(self) -> ta.Iterator[MarkedFn]:
        for ln in self.marked_pyasts_by_mark_lineno:
            fnr = self.FnResolver(self, ln)
            yield fnr.marked_fn


def test_gen():
    for file_name in glob.glob(__package__.split('.')[0] + '/**/*.py', recursive=True):
        mffr = MarkedFileFnResolver(file_name)
        for mf in mffr:
            nr = translate(mf.pyast)

            print(yaml.dump(sm.serialize(nr)))
            print()

            print(ren.render(nr))
            print()

            print()
