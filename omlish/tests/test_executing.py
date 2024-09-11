import ast
import inspect
import pprint
import textwrap
import typing as ta

import pytest

from .. import lang
from ..testing import pytest as ptu


if ta.TYPE_CHECKING:
    import executing
else:
    executing = lang.proxy_import('executing')


def check_equal(l, r):
    if l != r:
        def get_text_with_indentation(src: executing.Source, node: ast.AST) -> str:
            result = src.asttokens().get_text(node)
            if '\n' in result:
                result = ' ' * node.first_token.start[1] + result  # type: ignore
                result = textwrap.dedent(result)
            result = result.strip()
            return result

        call_frame = inspect.currentframe().f_back  # type: ignore
        call_node = executing.Source.executing(call_frame).node  # type: ignore
        source = executing.Source.for_frame(call_frame)  # type: ignore
        # breakpoint()
        sanitized_arg_strs = [
            get_text_with_indentation(source, arg)
            for arg in call_node.args  # type: ignore
        ]

        args = (l, r)
        pairs = list(zip(sanitized_arg_strs, args))

        _absent = object()

        def arg_prefix(arg):
            return f'{arg}: '

        def argument_to_string(obj: ta.Any) -> str:
            s = pprint.pformat(obj)
            s = s.replace('\\n', '\n')
            return s

        pairs = [(arg, argument_to_string(val)) for arg, val in pairs]

        def is_literal(s: str) -> bool:
            try:
                ast.literal_eval(s)
            except Exception:  # noqa
                return False
            return True

        pair_strs = [
            val if (is_literal(arg) or arg is _absent) else (arg_prefix(arg) + val)
            for arg, val in pairs
        ]

        ls, rs = pair_strs

        raise ValueError(f'{ls} != {rs}')


@ptu.skip_if_cant_import('executing')
def test_check_equal():
    def foo(x):
        return x + 1

    with pytest.raises(ValueError):  # noqa
        check_equal(foo(3) + 2, 8)
