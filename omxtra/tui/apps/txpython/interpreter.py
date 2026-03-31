import ast
import builtins
import io
import traceback

from omlish import check


##


class Interpreter:
    """
    Python interpreter that executes code without modifying global state.

    Execution is per-statement: the source is parsed into an AST and each statement is executed individually. The last
    statement, if it's a bare expression, is eval'd to capture its result (avoiding sys.displayhook). Output from
    print() is captured via a custom builtin in the namespace.
    """

    def __init__(self) -> None:
        super().__init__()

        self._output = io.StringIO()

        self.namespace: dict = {
            '__name__': '__console__',
            '__doc__': None,
            '__builtins__': self._make_builtins(),
        }

    def _make_builtins(self) -> dict:
        b = dict(vars(builtins))
        b['print'] = self._print
        return b

    def _print(self, *args, **kwargs):
        kwargs.setdefault('file', self._output)
        builtins.print(*args, **kwargs)

    def execute(self, source: str) -> tuple[str, str]:
        """Execute source code. Returns (output, errors)."""

        self._output = io.StringIO()

        # Parse to AST
        try:
            tree = compile(source, '<input>', 'exec', ast.PyCF_ONLY_AST)
        except (SyntaxError, OverflowError, ValueError) as e:
            return '', self._format_error(e)

        tree = check.isinstance(tree, ast.Module)

        if not tree.body:
            return '', ''

        *leading, last = tree.body

        # Execute all statements except the last
        for stmt in leading:
            err = self._exec_stmt(stmt)
            if err:
                return self._output.getvalue(), err

        # Last statement: eval if bare expression, exec otherwise
        if isinstance(last, ast.Expr):
            expr_node = ast.Expression(body=last.value)
            ast.copy_location(last, expr_node)
            ast.fix_missing_locations(expr_node)
            try:
                code_obj = compile(expr_node, '<input>', 'eval')
            except (SyntaxError, OverflowError, ValueError) as e:
                return self._output.getvalue(), self._format_error(e)
            try:
                result = eval(code_obj, self.namespace)  # noqa
                output = self._output.getvalue()
                if result is not None:
                    self.namespace['_'] = result
                    output += repr(result) + '\n'
                return output, ''
            except SystemExit:
                return self._output.getvalue(), 'Use Ctrl+D to exit.\n'
            except Exception as e:  # noqa
                return self._output.getvalue(), self._format_error(e)
        else:
            err = self._exec_stmt(last)
            return self._output.getvalue(), err or ''

    def _exec_stmt(self, stmt: ast.stmt) -> str:
        """Execute a single AST statement. Returns error string or empty."""

        mod = ast.Module(body=[stmt], type_ignores=[])
        ast.fix_missing_locations(mod)
        try:
            code_obj = compile(mod, '<input>', 'exec')
        except (SyntaxError, OverflowError, ValueError) as e:
            return self._format_error(e)
        try:
            exec(code_obj, self.namespace)
        except SystemExit:
            return 'Use Ctrl+D to exit.\n'
        except Exception as e:  # noqa
            return self._format_error(e)
        return ''

    def _format_error(self, exc: Exception) -> str:
        if isinstance(exc, SyntaxError):
            return ''.join(traceback.format_exception(type(exc), exc, None))
        tb = exc.__traceback__
        while tb is not None and tb.tb_frame.f_code.co_filename != '<input>':
            tb = tb.tb_next
        return ''.join(traceback.format_exception(type(exc), exc, tb))
