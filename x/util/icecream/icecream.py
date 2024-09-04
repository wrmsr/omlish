"""
IceCream - Never use print() to debug again

Ansgar Grunseid
grunseid.com
grunseid@gmail.com

License: MIT
"""
import ast
import contextlib
import datetime
import functools
import inspect
import os.path
import pprint
import sys
import textwrap
import types
import typing as ta
import warnings

import colorama
import executing
import pygments.formatters
import pygments.lexers

from .coloring import SolarizedDark


_absent = object()


_COLORIZE_FORMATTER = pygments.formatters.Terminal256Formatter(style=SolarizedDark)
_COLORIZE_LEXER = pygments.lexers.Python3Lexer(ensurenl=False)


def colorize(s: str) -> str:
    return pygments.highlight(s, _COLORIZE_LEXER, _COLORIZE_FORMATTER)


@contextlib.contextmanager
def support_terminal_colors_in_windows() -> ta.Iterator[None]:
    # Filter and replace ANSI escape sequences on Windows with equivalent Win32 API calls. This code does nothing on
    # non-Windows systems.
    colorama.init()
    yield
    colorama.deinit()


def stderr_print(*args: ta.Any) -> None:
    print(*args, file=sys.stderr)


def is_literal(s: str) -> bool:
    try:
        ast.literal_eval(s)
    except Exception:  # noqa
        return False
    return True


def colorized_stderr_print(s: str) -> None:
    colored = colorize(s)
    with support_terminal_colors_in_windows():
        stderr_print(colored)


DEFAULT_PREFIX = 'ic| '
DEFAULT_LINE_WRAP_WIDTH = 70  # Characters.
DEFAULT_CONTEXT_DELIMITER = '- '
DEFAULT_OUTPUT_FUNCTION = colorized_stderr_print
DEFAULT_ARG_TO_STRING_FUNCTION = pprint.pformat


# This info message is printed instead of the arguments when icecream fails to find or access source code that's
# required to parse and analyze. This can happen, for example, when
#
#   - ic() is invoked inside a REPL or interactive shell, e.g. from the command line (CLI) or with python -i.
#
#   - The source code is mangled and/or packaged, e.g. with a project freezer like PyInstaller.
#
#   - The underlying source code changed during execution. See https://stackoverflow.com/a/33175832.
NO_SOURCE_AVAILABLE_WARNING_MESSAGE = (
    'Failed to access the underlying source code for analysis. Was ic() invoked in a REPL (e.g. from the command line),'
    ' a frozen application (e.g. packaged with PyInstaller), or did the underlying source code change during execution?'
)


def call_or_value(obj: ta.Any) -> ta.Any:
    return obj() if callable(obj) else obj


class Source(executing.Source):
    def get_text_with_indentation(self, node: ast.AST) -> bool:
        result = self.asttokens().get_text(node)
        if '\n' in result:
            result = ' ' * node.first_token.start[1] + result
            result = textwrap.dedent(result)
        result = result.strip()
        return result


def prefix_lines(prefix: str, s: str, start_at_line: int = 0) -> list[str]:
    lines = s.splitlines()

    for i in range(start_at_line, len(lines)):
        lines[i] = prefix + lines[i]

    return lines


def prefix_first_line_indent_remaining(prefix: str, s: str) -> list[str]:
    indent = ' ' * len(prefix)
    lines = prefix_lines(indent, s, start_at_line=1)
    lines[0] = prefix + lines[0]
    return lines


def format_pair(prefix: str, arg: ta.Any, value: ta.Any) -> str:
    if arg is _absent:
        arg_lines = []
        value_prefix = prefix
    else:
        arg_lines = prefix_first_line_indent_remaining(prefix, arg)
        value_prefix = arg_lines[-1] + ': '

    looks_like_a_string = (value[0] + value[-1]) in ["''", '""']
    if looks_like_a_string:  # Align the start of multiline strings.
        value_lines = prefix_lines(' ', value, start_at_line=1)
        value = '\n'.join(value_lines)

    value_lines = prefix_first_line_indent_remaining(value_prefix, value)
    lines = arg_lines[:-1] + value_lines
    return '\n'.join(lines)


@functools.singledispatch
def argument_to_string(obj: ta.Any) -> str:
    s = DEFAULT_ARG_TO_STRING_FUNCTION(obj)
    s = s.replace('\\n', '\n')  # Preserve string newlines in output.
    return s


class IceCreamDebugger:
    _pair_delimiter = ', '  # Used by the tests in tests/.
    line_wrap_width = DEFAULT_LINE_WRAP_WIDTH
    context_delimiter = DEFAULT_CONTEXT_DELIMITER

    def __init__(
            self,
            *,
            prefix: str = DEFAULT_PREFIX,
            output_function: ta.Callable[[str], None] = DEFAULT_OUTPUT_FUNCTION,
            arg_to_string_function: ta.Callable[[ta.Any], str] = argument_to_string,
            include_context: bool = False,
            context_abs_path: bool = False,
    ) -> None:
        super().__init__()

        self._enabled = True
        self._prefix = prefix
        self._include_context = include_context
        self._output_function = output_function
        self._arg_to_string_function = arg_to_string_function
        self._context_abs_path = context_abs_path

    def __call__(self, *args):
        if self._enabled:
            call_frame = inspect.currentframe().f_back
            self._output_function(self._format(call_frame, *args))

        if not args:  # E.g. ic().
            passthrough = None
        elif len(args) == 1:  # E.g. ic(1).
            passthrough = args[0]
        else:  # E.g. ic(1, 2, 3).
            passthrough = args

        return passthrough

    def format(self, *args):
        call_frame = inspect.currentframe().f_back
        out = self._format(call_frame, *args)
        return out

    def _format(self, call_frame: types.FrameType, *args: ta.Any) -> str:
        prefix = call_or_value(self._prefix)

        context = self._format_context(call_frame)
        if not args:
            time = self._format_time()
            out = prefix + context + time
        else:
            if not self._include_context:
                context = ''
            out = self._format_args(call_frame, prefix, context, args)

        return out

    def _format_args(self, call_frame: types.FrameType, prefix: str, context: str, args: tuple) -> str:
        call_node = Source.executing(call_frame).node
        if call_node is not None:
            source = Source.for_frame(call_frame)
            sanitized_arg_strs = [
                source.get_text_with_indentation(arg)
                for arg in call_node.args
            ]
        else:
            warnings.warn(
                NO_SOURCE_AVAILABLE_WARNING_MESSAGE,
                category=RuntimeWarning,
                stacklevel=4,
            )
            sanitized_arg_strs = [_absent] * len(args)

        pairs = list(zip(sanitized_arg_strs, args))

        out = self._construct_argument_output(prefix, context, pairs)
        return out

    def _construct_argument_output(self, prefix: str, context: str, pairs: ta.Sequence[tuple[str, ta.Any]]) -> str:
        def arg_prefix(arg):
            return f'{arg}: '

        pairs = [(arg, self._arg_to_string_function(val)) for arg, val in pairs]
        # For cleaner output, if <arg> is a literal, eg 3, "a string", b'bytes', etc, only output the value, not the
        # argument and the value, because the argument and the value will be identical or nigh identical. Ex: with
        # ic("hello"), just output
        #
        #   ic| 'hello',
        #
        # instead of
        #
        #   ic| "hello": 'hello'.
        #
        # When the source for an arg is missing we also only print the value, since we can't know anything about the
        # argument itself.
        pair_strs = [
            val if (is_literal(arg) or arg is _absent)
            else (arg_prefix(arg) + val)
            for arg, val in pairs]

        all_args_on_one_line = self._pair_delimiter.join(pair_strs)
        multiline_args = len(all_args_on_one_line.splitlines()) > 1

        context_delimiter = self.context_delimiter if context else ''
        all_pairs = prefix + context + context_delimiter + all_args_on_one_line
        first_line_too_long = len(all_pairs.splitlines()[0]) > self.line_wrap_width

        if multiline_args or first_line_too_long:
            # ic| foo.py:11 in foo()
            #     multilineStr: 'line1
            #                    line2'
            #
            # ic| foo.py:11 in foo()
            #     a: 11111111111111111111
            #     b: 22222222222222222222
            if context:
                lines = [prefix + context] + [
                    format_pair(len(prefix) * ' ', arg, value)
                    for arg, value in pairs
                ]

            # ic| multilineStr: 'line1
            #                    line2'
            #
            # ic| a: 11111111111111111111
            #     b: 22222222222222222222
            else:
                arg_lines = [
                    format_pair('', arg, value)
                    for arg, value in pairs
                ]
                lines = prefix_first_line_indent_remaining(prefix, '\n'.join(arg_lines))

        # ic| foo.py:11 in foo()- a: 1, b: 2
        # ic| a: 1, b: 2, c: 3
        else:
            lines = [prefix + context + context_delimiter + all_args_on_one_line]

        return '\n'.join(lines)

    def _format_context(self, call_frame: types.FrameType) -> str:
        filename, line_number, parent_function = self._get_context(call_frame)

        if parent_function != '<module>':
            parent_function = f'{parent_function}()'

        context = f'{filename}:{line_number} in {parent_function}'
        return context

    def _format_time(self) -> str:
        now = datetime.datetime.now()  # noqa
        formatted = now.strftime('%H:%M:%S.%f')[:-3]
        return f' at {formatted}'

    def _get_context(self, call_frame: types.FrameType) -> tuple[str, int, str]:
        frame_info = inspect.getframeinfo(call_frame)
        line_number = frame_info.lineno
        parent_function = frame_info.function

        filepath = (os.path.realpath if self._context_abs_path else os.path.basename)(frame_info.filename)
        return filepath, line_number, parent_function

    def enable(self) -> None:
        self._enabled = True

    def disable(self) -> None:
        self._enabled = False


ic = IceCreamDebugger()
