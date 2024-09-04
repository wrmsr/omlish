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
import warnings

import colorama
import executing
import pygments.formatters
import pygments.lexers

from .coloring import SolarizedDark


_absent = object()


def bind_static_variable(name, value):
    def decorator(fn):
        setattr(fn, name, value)
        return fn
    return decorator


@bind_static_variable('formatter', pygments.formatters.Terminal256Formatter(style=SolarizedDark))
@bind_static_variable('lexer', pygments.lexers.Python3Lexer(ensurenl=False))
def colorize(s):
    self = colorize
    return pygments.highlight(s, self.lexer, self.formatter)


@contextlib.contextmanager
def support_terminal_colors_in_windows():
    # Filter and replace ANSI escape sequences on Windows with equivalent Win32 API calls. This code does nothing on
    # non-Windows systems.
    colorama.init()
    yield
    colorama.deinit()


def stderr_print(*args):
    print(*args, file=sys.stderr)


def is_literal(s):
    try:
        ast.literal_eval(s)
    except Exception:  # noqa
        return False
    return True


def colorized_stderr_print(s):
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
    'Failed to access the underlying source code for analysis. Was ic() '
    'invoked in a REPL (e.g. from the command line), a frozen application '
    '(e.g. packaged with PyInstaller), or did the underlying source code '
    'change during execution?'
)


def call_or_value(obj):
    return obj() if callable(obj) else obj


class Source(executing.Source):
    def get_text_with_indentation(self, node):
        result = self.asttokens().get_text(node)
        if '\n' in result:
            result = ' ' * node.first_token.start[1] + result
            result = textwrap.dedent(result)
        result = result.strip()
        return result


def prefix_lines(prefix, s, start_at_line=0):
    lines = s.splitlines()

    for i in range(start_at_line, len(lines)):
        lines[i] = prefix + lines[i]

    return lines


def prefix_first_line_indent_remaining(prefix, s):
    indent = ' ' * len(prefix)
    lines = prefix_lines(indent, s, start_at_line=1)
    lines[0] = prefix + lines[0]
    return lines


def format_pair(prefix, arg, value):
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


def singledispatch(func):
    func = functools.singledispatch(func)

    # add unregister based on https://stackoverflow.com/a/25951784
    closure = dict(zip(func.register.__code__.co_freevars, func.register.__closure__))

    registry = closure['registry'].cell_contents
    dispatch_cache = closure['dispatch_cache'].cell_contents

    def unregister(cls):
        del registry[cls]
        dispatch_cache.clear()

    func.unregister = unregister
    return func


@singledispatch
def argument_to_string(obj):
    s = DEFAULT_ARG_TO_STRING_FUNCTION(obj)
    s = s.replace('\\n', '\n')  # Preserve string newlines in output.
    return s


class IceCreamDebugger:
    _pair_delimiter = ', '  # Used by the tests in tests/.
    line_wrap_width = DEFAULT_LINE_WRAP_WIDTH
    context_delimiter = DEFAULT_CONTEXT_DELIMITER

    def __init__(
            self,
            prefix=DEFAULT_PREFIX,
            output_function=DEFAULT_OUTPUT_FUNCTION,
            arg_to_string_function=argument_to_string,
            include_context=False,
            context_abs_path=False,
    ):
        super().__init__()
        self.enabled = True
        self.prefix = prefix
        self.include_context = include_context
        self.output_function = output_function
        self.arg_to_string_function = arg_to_string_function
        self.context_abs_path = context_abs_path

    def __call__(self, *args):
        if self.enabled:
            call_frame = inspect.currentframe().f_back
            self.output_function(self._format(call_frame, *args))

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

    def _format(self, call_frame, *args):
        prefix = call_or_value(self.prefix)

        context = self._format_context(call_frame)
        if not args:
            time = self._format_time()
            out = prefix + context + time
        else:
            if not self.include_context:
                context = ''
            out = self._format_args(
                call_frame, prefix, context, args)

        return out

    def _format_args(self, call_frame, prefix, context, args):
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

    def _construct_argument_output(self, prefix, context, pairs):
        def arg_prefix(arg):
            return f'{arg}: '

        pairs = [(arg, self.arg_to_string_function(val)) for arg, val in pairs]
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

    def _format_context(self, call_frame):
        filename, line_number, parent_function = self._get_context(call_frame)

        if parent_function != '<module>':
            parent_function = f'{parent_function}()'

        context = f'{filename}:{line_number} in {parent_function}'
        return context

    def _format_time(self):
        now = datetime.datetime.now()  # noqa
        formatted = now.strftime('%H:%M:%S.%f')[:-3]
        return f' at {formatted}'

    def _get_context(self, call_frame):
        frame_info = inspect.getframeinfo(call_frame)
        line_number = frame_info.lineno
        parent_function = frame_info.function

        filepath = (os.path.realpath if self.context_abs_path else os.path.basename)(frame_info.filename)
        return filepath, line_number, parent_function

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def configure_output(
            self,
            prefix=_absent,
            output_function=_absent,
            arg_to_string_function=_absent,
            include_context=_absent,
            context_abs_path=_absent,
    ):
        if all(k is _absent for k in (prefix, output_function, arg_to_string_function, include_context, context_abs_path)):  # noqa
            raise TypeError('configure_output() missing at least one argument')

        if prefix is not _absent:
            self.prefix = prefix

        if output_function is not _absent:
            self.output_function = output_function

        if arg_to_string_function is not _absent:
            self.arg_to_string_function = arg_to_string_function

        if include_context is not _absent:
            self.include_context = include_context

        if context_abs_path is not _absent:
            self.context_abs_path = context_abs_path


ic = IceCreamDebugger()
