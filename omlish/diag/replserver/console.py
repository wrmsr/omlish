"""
import sys, threading, pdb, functools
def _attach(repl):
    frame = sys._current_frames()[threading.enumerate()[0].ident]
    debugger = pdb.Pdb(
        stdin=repl.conn.makefile('r'),
        stdout=repl.conn.makefile('w'),
    )
    debugger.reset()
    while frame:
        frame.f_trace = debugger.trace_dispatch
        debugger.botframe = frame
        frame = frame.f_back
    debugger.set_step()
    frame.f_trace = debugger.trace_dispatch
"""
import ast
import codeop
import errno
import logging
import socket as sock
import sys
import threading
import traceback
import types
import typing as ta

from ... import check


log = logging.getLogger(__name__)


##


class DisconnectError(Exception):
    pass


class InteractiveSocketConsole:
    """code.InteractiveConsole but just different enough to not be worth subclassing."""

    ENCODING = 'utf-8'

    def __init__(
            self,
            conn: sock.socket,
            locals: dict[str, ta.Any] | None = None,  # noqa
            filename: str = '<console>',
    ) -> None:
        super().__init__()

        if locals is None:
            locals = {  # noqa
                '__name__': '__console__',
                '__doc__': None,
                '__console__': self,
            }

        self._conn = conn
        self._locals = locals
        self._filename = filename

        self._compiler = codeop.CommandCompiler()
        self._buffer: list[str] = []
        self._count = 0
        self._write_count = -1

    def reset_buffer(self) -> None:
        self._buffer = []

    @property
    def conn(self) -> sock.socket:
        return self._conn

    CPRT = 'Type "help", "copyright", "credits" or "license" for more information.'

    def interact(self, banner: str | None = None, exitmsg: str | None = None) -> None:
        log.info('Console %x on thread %r interacting', id(self), threading.current_thread().ident)

        try:
            ps1 = getattr(sys, 'ps1', '>>> ')
            ps2 = getattr(sys, 'ps2', '... ')

            if banner is None:
                self.write(f'Python {sys.version} on {sys.platform}\n{self.CPRT}\n({self.__class__.__name__})\n')
            elif banner:
                self.write(f'{banner!s}\n')

            more = False
            while True:
                try:
                    try:
                        line = self.raw_input(ps2 if more else ps1)
                    except EOFError:
                        self.write('\n')
                        break
                    else:
                        more = self.push_line(line)

                except KeyboardInterrupt:
                    self.write('\nKeyboardInterrupt\n')
                    self.reset_buffer()
                    more = False

            if exitmsg is None:
                self.write(f'now exiting {self.__class__.__name__}...\n')

            elif exitmsg != '':
                self.write(f'{exitmsg}\n')

        except DisconnectError:
            pass

        except OSError as oe:
            if oe.errno == errno.EBADF:
                pass

        finally:
            log.info('Console %x on thread %r finished', id(self), threading.current_thread().ident)

    def push_line(self, line: str) -> bool:
        self._buffer.append(line)
        source = '\n'.join(self._buffer)
        more = self.run_source(source, self._filename)
        if not more:
            self.reset_buffer()
        return more

    def raw_input(self, prompt: str = '') -> str:
        self.write(prompt)
        buf = b''
        while True:
            b = self._conn.recv(1)
            if not b:
                raise DisconnectError
            if b == b'\n':
                break
            buf += b
        return buf.decode(self.ENCODING)

    def write(self, data: str) -> None:
        self._conn.send(data.encode(self.ENCODING))

    def compile(
            self,
            source: str | ast.AST,
            filename: str = '<input>',
            symbol: str = 'single',
    ) -> types.CodeType | None:
        if isinstance(source, ast.AST):
            return self._compiler.compiler(source, filename, symbol)  # type: ignore
        else:
            return self._compiler(source, filename, symbol)

    def run_source(
            self,
            source: str | ast.AST,
            filename: str = '<input>',
            symbol: str = 'single',
    ) -> bool:
        try:
            code = self.compile(source, filename, symbol)
        except (OverflowError, SyntaxError, ValueError):
            # Case 1 (incorrect)
            self.show_syntax_error(filename)
            return False

        if code is None:
            # Case 2 (incomplete)
            return True

        # Case 3 (complete)
        try:
            node = ast.parse(source)  # type: ignore
        except (OverflowError, SyntaxError, ValueError):
            return True

        if (
                isinstance(node, ast.Module) and
                node.body and
                isinstance(node.body[-1], ast.Expr)
        ):
            expr = node.body[-1]
            source = ast.Interactive(
                [
                    *node.body[:-1],
                    ast.Assign(
                        [ast.Name(
                            f'_{self._count}',
                            ast.Store(),
                            lineno=expr.lineno,
                            col_offset=expr.col_offset,
                        )],
                        expr.value,
                        lineno=expr.lineno,
                        col_offset=expr.col_offset,
                    ),
                ],
            )
            ast.fix_missing_locations(source)
            self._write_count = self._count

        code = check.not_none(self.compile(source, filename, symbol))
        self.run_code(code)
        return False

    def run_code(self, code: types.CodeType) -> None:
        try:
            exec(code, self._locals)
        except SystemExit:
            raise
        except Exception:  # noqa
            self.show_traceback()
        else:
            if self._count == self._write_count:
                self.write(repr(self._locals[f'_{self._count}']))
                self.write('\n')
                self._count += 1

    def show_traceback(self) -> None:
        sys.last_type, sys.last_value, last_tb = ei = sys.exc_info()
        sys.last_traceback = last_tb
        try:
            lines = traceback.format_exception(ei[0], ei[1], last_tb.tb_next)  # type: ignore
            self.write(''.join(lines))
        finally:
            last_tb = ei = None  # type: ignore  # noqa

    def show_syntax_error(self, filename: str | None = None) -> None:
        et, e, tb = sys.exc_info()
        sys.last_type = et
        sys.last_value = e
        sys.last_traceback = tb
        if filename and et is SyntaxError:
            # Work hard to stuff the correct filename in the exception
            try:
                msg, (dummy_filename, lineno, offset, line) = e.args  # type: ignore
            except ValueError:
                # Not the format we expect; leave it alone
                pass
            else:
                # Stuff in the right filename
                e = SyntaxError(msg, (filename, lineno, offset, line))
                sys.last_value = e
        lines = traceback.format_exception_only(et, e)
        self.write(''.join(lines))
