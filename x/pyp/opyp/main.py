# ruff: noqa: N802
"""
https://github.com/hauntsaninja/pyp/tree/5af2a583fcac2e0f57272ee2112eb76cb0449191
"""
import argparse
import ast
import sys
import traceback

from omlish import check

from .asts import dfs_walk
from .config import PypConfig
from .errors import PypError
from .transform import PypTransform


def run_pyp(args: argparse.Namespace) -> None:
    config = PypConfig()
    tree = PypTransform(
        args.before,
        args.code,
        args.after,
        args.define_pypprint,
        config,
    ).build()

    if args.explain:
        print(config.shebang)
        print(ast.unparse(tree))
        return

    try:
        exec(compile(tree, filename='<pyp>', mode='exec'), {})

    except Exception as e:
        # On error, reconstruct a traceback into the generated code
        # Also add some diagnostics for ModuleNotFoundError and NameError
        try:
            line_to_node: dict[int, ast.AST] = {}
            for node in dfs_walk(tree):
                line_to_node.setdefault(getattr(node, 'lineno', -1), node)

            def code_for_line(lineno: int) -> str:
                node = line_to_node[lineno]
                # Don't unparse nested child statements. Note this destroys the tree.
                for _, value in ast.iter_fields(node):
                    if isinstance(value, list) and value and isinstance(value[0], ast.stmt):
                        value.clear()
                return ast.unparse(node).strip()

            # Time to commit several sins against CPython implementation details
            tb_except = traceback.TracebackException(type(e), e, e.__traceback__.tb_next)  # type: ignore
            for fs in tb_except.stack:
                if fs.filename == '<pyp>':
                    if fs.lineno is None:
                        raise RuntimeError('When would this happen?')  # noqa

                    if sys.version_info >= (3, 13):
                        fs._lines = code_for_line(fs.lineno)  # type: ignore[attr-defined]  # noqa
                        fs.colno = None
                        fs.lineno = 'PYP_REDACTED'  # type: ignore[assignment]
                    else:
                        fs._line = code_for_line(fs.lineno)  # type: ignore[attr-defined]  # noqa
                        fs.lineno = 'PYP_REDACTED'  # type: ignore[assignment]

            tb_format = tb_except.format()
            check.in_('Traceback (most recent call last)', next(tb_format))

            message = 'Possible reconstructed traceback (most recent call last):\n'
            message += ''.join(tb_format).strip('\n')
            message = message.replace(', line PYP_REDACTED', '')
        except Exception:  # noqa
            message = ''.join(traceback.format_exception_only(type(e), e)).strip()

        if isinstance(e, ModuleNotFoundError):
            message += (
                '\n\nNote pyp treats undefined names as modules to automatically import. Perhaps you forgot to define '
                'something or PYP_CONFIG_PATH is set incorrectly?'
            )

        if args.before and isinstance(e, NameError):
            var = str(e)
            var = var[var.find("'") + 1 : var.rfind("'")]
            if var in ('lines', 'stdin'):
                message += (
                    '\n\nNote code in `--before` runs before any magic variables are defined and should not process '
                    'input. Your command should work by simply removing `--before`, so instead passing in multiple '
                    'statements in the main section of your code.'
                )

        raise PypError(
            'Code raised the following exception, consider using --explain to investigate:\n\n'
            f'{message}',
        ) from e


def parse_options(args: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog='pyp',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "Easily run Python at the shell!\n\n"
            "For help and examples, see https://github.com/hauntsaninja/pyp\n\n"
            "Cheatsheet:\n"
            "- Use `x`, `l` or `line` for a line in the input. Use `i`, `idx` or `index` "
            "for the index\n"
            "- Use `lines` to get a list of rstripped lines\n"
            "- Use `stdin` to get sys.stdin\n"
            "- Use print explicitly if you don't like when or how or what pyp's printing\n"
            "- If the magic is ever too mysterious, use --explain"
        ),
    )
    parser.add_argument('code', nargs='+', help='Python you want to run')
    parser.add_argument(
        '--explain',
        '--script',
        action='store_true',
        help='Prints the Python that would get run, instead of running it',
    )
    parser.add_argument(
        '-b',
        '--before',
        action='append',
        default=[],
        metavar='CODE',
        help='Python to run before processing input',
    )
    parser.add_argument(
        '-a',
        '--after',
        action='append',
        default=[],
        metavar='CODE',
        help='Python to run after processing input',
    )
    parser.add_argument(
        '--define-pypprint',
        action='store_true',
        help='Defines pypprint, if used, instead of importing it from pyp.',
    )
    return parser.parse_args(args)


def main() -> None:
    try:
        run_pyp(parse_options(sys.argv[1:]))
    except PypError as e:
        print(f'error: {e}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
