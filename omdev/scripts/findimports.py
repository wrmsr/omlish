#!/usr/bin/env python3
"""
TODO:
 - multiple commands:
  - dumb cmp (a = set(sys.modules); import ...; print(set(sys.modules) - a)
"""
import ast
import importlib.machinery
import importlib.util
import os.path
import sys


_BUILTIN_MODULE_NAMES = frozenset([*sys.builtin_module_names, *sys.stdlib_module_names])


def _main() -> None:
    def handle(fp: str) -> None:
        def rec(n):
            nodes.append(n)
            for c in ast.iter_child_nodes(n):
                rec(c)
        # if not os.path.isfile(os.path.join(os.path.dirname(fp), '__init__.py')):
        #     return
        with open(fp, 'r') as f:
            buf = f.read()
        nodes: list[ast.AST] = []
        rec(ast.parse(buf))
        imps.update(na.name for i in nodes if isinstance(i, ast.Import) for na in i.names)
        imps.update(i.module for i in nodes if isinstance(i, ast.ImportFrom) if i.module and not i.level)

    imps: set[str] = set()
    for rootp in sys.argv[1:]:
        if os.path.isfile(rootp):
            if rootp.endswith('.py'):
                handle(os.path.join(os.path.dirname(rootp), os.path.basename(rootp)))
        else:
            for dp, dns, fns in os.walk(os.path.expanduser(rootp)):  # noqa
                for fn in fns:
                    if fn.endswith('.py'):
                        handle(os.path.join(dp, fn))

    def whichmod(i: str) -> str:
        try:
            l = importlib.util.find_spec(i)
        except (ImportError, ValueError):
            return 'bad'
        if not isinstance(l, importlib.machinery.ModuleSpec) or not l.origin:
            return 'bad'
        # if l.origin.startswith(sys.base_prefix) or l.origin == 'frozen':
        #     return 'builtin'
        if i in _BUILTIN_MODULE_NAMES:
            return 'builtin'
        return 'dep'

    eimps = {n for n in imps for n in [n.split('.')[0]] if n not in sys.builtin_module_names}
    deps = {i for i in eimps if whichmod(i) != 'builtin'}
    print(chr(10).join(sorted(deps)))


if __name__ == '__main__':
    _main()
