import ast
import dataclasses as dc
import inspect
import pprint
import textwrap
import types
import typing as ta

from .. import lang


if ta.TYPE_CHECKING:
    import executing
else:
    executing = lang.proxy_import('executing')


class ArgsRenderer:
    """
    TODO:
     - kwargs
     - recursion
     - whatever pytest looks like
     - make sure not leaking sensitive data
    """

    def __init__(
            self,
            origin: types.TracebackType | types.FrameType | None = None,
            back: int = 1,
    ) -> None:
        super().__init__()

        self._origin = origin

        self._frame: types.FrameType | None
        if isinstance(origin, types.TracebackType):
            self._frame = origin.tb_frame
        elif isinstance(origin, types.FrameType):
            self._frame = origin
        elif origin is None:
            frame = inspect.currentframe()
            for _ in range(back + 1):
                if frame is None:
                    break
                frame = frame.f_back
            self._frame = frame
        else:
            raise TypeError(origin)

    def _get_indented_text(
            self,
            src: executing.Source,
            node: ast.AST,
    ) -> str:
        result = src.asttokens().get_text(node)
        if '\n' in result:
            result = ' ' * node.first_token.start[1] + result  # type: ignore
            result = textwrap.dedent(result)
        result = result.strip()
        return result

    def _val_to_string(self, obj: ta.Any) -> str:
        s = pprint.pformat(obj)
        s = s.replace('\\n', '\n')
        return s

    def _is_literal_expr(self, s: str) -> bool:
        try:
            ast.literal_eval(s)
        except Exception:  # noqa
            return False
        return True

    @dc.dataclass(frozen=True)
    class RenderedArg:
        val: str
        expr: str
        is_literal_expr: bool

        def __str__(self) -> str:
            if self.is_literal_expr:
                return self.val
            else:
                return f'({self.expr} = {self.val})'

    def render_args(
            self,
            *vals: ta.Any,
    ) -> ta.Sequence[RenderedArg] | None:
        if self._frame is None:
            return None

        call_node = executing.Source.executing(self._frame).node
        if not isinstance(call_node, ast.Call):
            return None

        source = executing.Source.for_frame(self._frame)

        exprs = [
            self._get_indented_text(source, arg)  # noqa
            for arg in call_node.args
        ]
        if len(exprs) != len(vals):
            return None

        return [
            self.RenderedArg(
                val=self._val_to_string(val),
                expr=expr,
                is_literal_expr=self._is_literal_expr(expr),
            )
            for val, expr in zip(vals, exprs)
        ]

    @classmethod
    def smoketest(cls) -> bool:
        def bar(z):
            return z + 1

        def foo(x, y):
            return cls().render_args(x, y)

        r = foo(1, bar(2))
        if r is None:
            return False

        x, y = r
        return (
            x == cls.RenderedArg(val='1', expr='1', is_literal_expr=True) and
            y == cls.RenderedArg(val='3', expr='bar(2)', is_literal_expr=False)
        )
