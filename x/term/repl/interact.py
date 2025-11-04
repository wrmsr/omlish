#   Copyright 2000-2010 Michael Hudson-Doyle <micahel@gmail.com>
#                        Armin Rigo
#
#                    All Rights Reserved
#
#
# Permission to use, copy, modify, and distribute this software and its documentation for any purpose is hereby granted
# without fee, provided that the above copyright notice appear in all copies and that both that copyright notice and
# this permission notice appear in supporting documentation.
#
# THE AUTHOR MICHAEL HUDSON DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS, IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES
# OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
"""
This is an alternative to python_reader which tries to emulate the CPython prompt as closely as possible, with the
exception of allowing multiline input and multiline history entries.
"""
import _sitebuiltins
import functools
import os
import sys
import traceback
import typing as ta
import warnings

from omlish import check

from .console import CONSOLE_ERROR_TYPES
from .readline import _get_reader
from .readline import append_history_file
from .readline import multiline_input


##


def check_init() -> str:
    """Returns the error message if there is a problem initializing the state."""

    try:
        _get_reader()
    except CONSOLE_ERROR_TYPES as e:
        if term := os.environ.get('TERM', ''):
            term = f'; TERM={term}'
        return str(str(e) or repr(e) or 'unknown error') + term
    return ''


def _strip_final_indent(text: str) -> str:
    # kill spaces and tabs at the end, but only if they follow '\n'. meant to remove the auto-indentation only (although
    # it would of course also remove explicitly-added indentation).
    short = text.rstrip(' \t')
    n = len(short)
    if n > 0 and text[n - 1] == '\n':
        return short
    return text


def _clear_screen() -> None:
    reader = _get_reader()
    reader.scheduled_commands.append('clear_screen')


REPL_COMMANDS: ta.Mapping[str, ta.Any] = {
    'exit': _sitebuiltins.Quitter('exit', ''),
    'quit': _sitebuiltins.Quitter('quit' ,''),
    'copyright': _sitebuiltins._Printer('copyright', sys.copyright),  # noqa
    'help': _sitebuiltins._Helper(),  # noqa
    'clear': _clear_screen,
    '\x1a': _sitebuiltins.Quitter('\x1a', ''),
}


def _more_lines(console: 'InteractiveConsole', unicodetext: str) -> bool:
    src = _strip_final_indent(unicodetext)
    if src.startswith('/') and '\n' not in src:
        return False

    lines = src.splitlines(keepends=True)
    if not lines:
        return False

    last_line = lines[-1]
    was_indented = last_line.startswith((' ', '\t'))
    not_empty = last_line.strip() != ''
    incomplete = not last_line.endswith('\n')
    return (was_indented or not_empty) and incomplete


class InteractiveConsole:
    def __init__(self) -> None:
        super().__init__()

        self.resetbuffer()

    def resetbuffer(self):
        """Reset the input buffer."""

        self.buffer = []

    def write(self, data):
        """
        Write a string.

        The base implementation writes to sys.stderr; a subclass may replace this with a different implementation.
        """

        sys.stderr.write(data)

    def showtraceback(self):
        """Display the exception that just occurred.

        We remove the first stack item because it is our own code.

        The output is written by self.write(), below.

        """
        try:
            typ, value, tb = sys.exc_info()
            self._showtraceback(typ, value, check.not_none(tb).tb_next, '')
        finally:
            typ = value = tb = None

    def push(self, line):
        """
        Push a line to the interpreter.

        The line should not have a trailing newline; it may have internal newlines. The line is appended to a buffer and
        the interpreter's runsource() method is called with the concatenated contents of the buffer as source. If this
        indicates that the command was executed or invalid, the buffer is reset; otherwise, the command is incomplete,
        and the buffer is left as it was after the line was appended. The return value is 1 if more input is required, 0
        if the line was dealt with in some way (this is the same as runsource()).
        """

        self.buffer.append(line)
        return False

    def _showtraceback(self, typ, value, tb, source):
        sys.last_type = typ
        sys.last_traceback = tb

        value = value.with_traceback(tb)

        # Set the line of text that the exception refers to
        lines = source.splitlines()
        if (
                source and typ is SyntaxError and
                not value.text and value.lineno is not None and
                len(lines) >= value.lineno
        ):
            value.text = lines[value.lineno - 1]

        sys.last_exc = sys.last_value = value = value.with_traceback(tb)

        if sys.excepthook is sys.__excepthook__:
            self._excepthook(typ, value, tb)

        else:
            # If someone has set sys.excepthook, we let that take precedence over self.write
            try:
                sys.excepthook(typ, value, tb)
            except SystemExit:
                raise
            except BaseException as e:  # noqa
                e.__context__ = None

                e = e.with_traceback(check.not_none(e.__traceback__).tb_next)
                print('Error in sys.excepthook:', file=sys.stderr)

                sys.__excepthook__(type(e), e, e.__traceback__)
                print(file=sys.stderr)
                print('Original exception was:', file=sys.stderr)

                sys.__excepthook__(typ, value, tb)

    def _excepthook(self, typ, value, tb):
        # This method is being overwritten in _pyrepl.console.InteractiveColoredConsole
        lines = traceback.format_exception(typ, value, tb)
        self.write(''.join(lines))


def run_multiline_interactive_console(console: InteractiveConsole) -> None:
    # from .readline import _setup
    # _setup()

    # if future_flags:
    #     console.compile.compiler.flags |= future_flags

    more_lines = functools.partial(_more_lines, console)
    input_n = 0

    def maybe_run_command(statement: str) -> bool:
        statement = statement.strip()
        if '\n' in statement or not statement.startswith('/'):
            return False

        cmd = statement[1:]
        if cmd not in REPL_COMMANDS:
            return False

        reader = _get_reader()
        reader.history.pop()  # skip internal commands in history

        command = REPL_COMMANDS[cmd]
        if callable(command):
            # Make sure that history does not change because of commands
            with reader.suspend_history():
                command()
            return True

        return False

    while True:
        try:
            try:
                sys.stdout.flush()
            except Exception:  # noqa
                pass

            ps1 = getattr(sys, 'ps1', '>>> ')
            ps2 = getattr(sys, 'ps2', '... ')
            try:
                statement = multiline_input(more_lines, ps1, ps2)
            except EOFError:
                break

            if maybe_run_command(statement):
                continue

            more = console.push(_strip_final_indent(statement))
            check.state(not more)
            try:
                append_history_file()
            except (FileNotFoundError, PermissionError, OSError) as e:
                warnings.warn(f'failed to open the history file for writing: {e}')

            input_n += 1

        except KeyboardInterrupt:
            r = _get_reader()
            r.cmpltn_reset()
            if r.input_trans is r.isearch_trans:
                r.do_cmd(('isearch-end', ['']))
            r.set_pos(len(r.get_unicode()))
            r.set_dirty()
            r.refresh()
            console.write('\nKeyboardInterrupt\n')
            console.resetbuffer()

        except MemoryError:
            console.write('\nMemoryError\n')
            console.resetbuffer()

        except SystemExit:
            raise

        except BaseException as e:  # noqa
            console.showtraceback()
            console.resetbuffer()
