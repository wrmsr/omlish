import ast
import importlib.machinery
import importlib.util
import os.path
import sys


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
        for dp, dns, fns in os.walk(os.path.expanduser(rootp)):
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
        if l.origin.startswith(sys.base_prefix):
            return 'builtin'
        return 'dep'

    eimps = {n for n in imps for n in [n.split('.')[0]] if n not in sys.builtin_module_names}
    deps = {i for i in eimps if whichmod(i) != 'builtin'}
    print(chr(10).join(sorted(deps)))


if __name__ == '__main__':
    _main()
