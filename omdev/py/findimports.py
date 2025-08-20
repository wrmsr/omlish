#!/usr/bin/env python3
# @omlish-script
"""
Note: Not lite as supporting old ast grammars is annoying and a non-goal.

TODO:
 - !! FIX: from omlish import lang - try lang as a subpackage
 - multiple commands:
  - dumb cmp (a = set(sys.modules); import ...; print(set(sys.modules) - a)
 - graphviz
"""
import ast
import dataclasses as dc
import importlib.machinery
import importlib.util
import os.path
import sys
import typing as ta


##


class ImportFinder:
    def __init__(
            self,
            *,
            builtin_module_names: ta.AbstractSet[str] | None = None,
    ) -> None:
        super().__init__()

        if builtin_module_names is None:
            builtin_module_names = self.DEFAULT_BUILTIN_MODULE_NAMES
        self._builtin_module_names = builtin_module_names

        self._whichmod_cache: dict[str, ta.Any] = {}

    #

    @dc.dataclass(frozen=True)
    class Import:
        fp: str
        node: ast.AST
        line: str | None

    def yield_file_imports(self, fp: str) -> ta.Iterator[Import]:
        # if not os.path.isfile(os.path.join(os.path.dirname(fp), '__init__.py')):
        #     return

        with open(fp) as f:
            buf = f.read()

        lines = buf.splitlines(keepends=True)

        for node in ast.walk(ast.parse(buf)):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                yield ImportFinder.Import(
                    fp,
                    node,
                    lines[node.lineno - 1] if node.lineno is not None else None,
                )

    def yield_imports(self, *rootps: str) -> ta.Iterator[Import]:
        for rootp in rootps:
            if os.path.isfile(rootp):
                if rootp.endswith('.py'):
                    yield from self.yield_file_imports(os.path.join(os.path.dirname(rootp), os.path.basename(rootp)))

            else:
                for dp, dns, fns in os.walk(os.path.expanduser(rootp)):  # noqa
                    for fn in fns:
                        if fn.endswith('.py'):
                            yield from self.yield_file_imports(os.path.join(dp, fn))

    #

    def get_import_node_targets(self, node: ast.AST) -> set[str] | None:
        if isinstance(node, ast.Import):
            return {na.name for na in node.names}

        elif isinstance(node, ast.ImportFrom):
            return {node.module} if node.module and not node.level else set()

        else:
            return None

    def find_import_targets(self, *rootps: str) -> set[str]:
        ret: set[str] = set()
        for imp in self.yield_imports(*rootps):
            if (imp_tgts := self.get_import_node_targets(imp.node)):
                ret.update(imp_tgts)
        return ret

    #

    DEFAULT_BUILTIN_MODULE_NAMES: ta.ClassVar[ta.AbstractSet[str]] = frozenset([
        *sys.builtin_module_names,
        *sys.stdlib_module_names,
    ])

    def _whichmod(self, i: str) -> ta.Literal['bad', 'builtin', 'dep']:
        try:
            l = importlib.util.find_spec(i)
        except (ImportError, ValueError):
            return 'bad'

        if not isinstance(l, importlib.machinery.ModuleSpec) or not l.origin:
            return 'bad'

        # if l.origin.startswith(sys.base_prefix) or l.origin == 'frozen':
        #     return 'builtin'

        if i in self._builtin_module_names:
            return 'builtin'

        return 'dep'

    def whichmod(self, i: str) -> ta.Literal['bad', 'builtin', 'dep']:
        try:
            return self._whichmod_cache[i]
        except KeyError:
            pass

        ret = self._whichmod(i)
        self._whichmod_cache[i] = ret
        return ret

    def get_import_deps(self, imps: set[str]) -> set[str]:
        eimps = {n for n in imps for n in [n.split('.')[0]] if n not in sys.builtin_module_names}
        return {i for i in eimps if self.whichmod(i) != 'builtin'}


##


# @omlish-manifest
_CLI_MODULE = {'!.cli.types.CliModule': {
    'name': 'py/findimports',
    'module': __name__,
}}


if __name__ == '__main__':
    def _main() -> None:
        imp_finder = ImportFinder()
        imps = imp_finder.find_import_targets(*sys.argv[1:])
        deps = imp_finder.get_import_deps(imps)
        print(chr(10).join(sorted(deps)))

    _main()
