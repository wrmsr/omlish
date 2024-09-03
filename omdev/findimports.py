#!/usr/bin/env python3
# @omlish-script
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
import typing as ta


_BUILTIN_MODULE_NAMES = frozenset([*sys.builtin_module_names, *sys.stdlib_module_names])


def whichmod(i: str) -> ta.Literal['bad', 'builtin', 'dep']:
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


def yield_imports(fp: str) -> set[str]:
    # if not os.path.isfile(os.path.join(os.path.dirname(fp), '__init__.py')):
    #     return

    with open(fp) as f:
        buf = f.read()

    nodes: list[ast.AST] = []

    def rec(n):
        nodes.append(n)
        for c in ast.iter_child_nodes(n):
            rec(c)

    rec(ast.parse(buf))

    return {
        *(na.name for i in nodes if isinstance(i, ast.Import) for na in i.names),
        *(i.module for i in nodes if isinstance(i, ast.ImportFrom) if i.module and not i.level),
    }


def find_imports(*rootps: str) -> set[str]:
    imps: set[str] = set()

    for rootp in rootps:
        if os.path.isfile(rootp):
            if rootp.endswith('.py'):
                imps.update(yield_imports(os.path.join(os.path.dirname(rootp), os.path.basename(rootp))))

        else:
            for dp, dns, fns in os.walk(os.path.expanduser(rootp)):  # noqa
                for fn in fns:
                    if fn.endswith('.py'):
                        imps.update(yield_imports(os.path.join(dp, fn)))

    return imps


def get_import_deps(imps: set[str]) -> set[str]:
    eimps = {n for n in imps for n in [n.split('.')[0]] if n not in sys.builtin_module_names}
    return {i for i in eimps if whichmod(i) != 'builtin'}


def _main() -> None:
    imps = find_imports(*sys.argv[1:])
    deps = get_import_deps(imps)
    print(chr(10).join(sorted(deps)))


if __name__ == '__main__':
    _main()
