# Copyright (C) 2018 Alec Thomas
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# https://github.com/alecthomas/pawk/blob/d60f78399e8a01857ebd73415a00e7eb424043ab/pawk.py
"""cat input | pawk [<options>] <expr>

A Python line-processor (like awk).

See https://github.com/alecthomas/pawk for details. Based on
http://code.activestate.com/recipes/437932/.
"""
import argparse
import ast
import codecs
import contextlib
import inspect
import itertools
import os
import re
import sys
import types
import typing as ta

from omlish import check

from ...cli import CliModule


##


RESULT_VAR_NAME = '__result'

STRING_ESCAPE = 'unicode_escape'


# Store the last expression, if present, into variable var_name.
def save_last_expression(
        tree: ast.Module,
        var_name: str = RESULT_VAR_NAME,
) -> ast.Module:
    body = tree.body

    node: ast.AST | None = body[-1] if len(body) else None

    body.insert(
        0,
        ast.Assign(
            targets=[
                ast.Name(
                    id=var_name,
                    ctx=ast.Store(),
                ),
            ],
            value=ast.Constant(None),
        ),
    )

    if node is not None and isinstance(node, ast.Expr):
        body[-1] = ast.copy_location(
            ast.Assign(
                targets=[
                    ast.Name(
                        id=var_name,
                        ctx=ast.Store(),
                    ),
                ],
                value=node.value,
            ),
            node,  # noqa
        )

    return ast.fix_missing_locations(tree)


def compile_command(text: str) -> types.CodeType:
    mod = check.isinstance(compile(text, 'EXPR', 'exec', flags=ast.PyCF_ONLY_AST), ast.Module)
    tree = save_last_expression(mod)
    return compile(tree, 'EXPR', 'exec')


def eval_in_context(
        codeobj: types.CodeType,
        context: 'Context',
        var_name: str = RESULT_VAR_NAME,
) -> ta.Any:
    exec(codeobj, globals(), context)
    return context.pop(var_name, None)


class Action:
    """Represents a single action to be applied to each line."""

    def __init__(
            self,
            pattern: str | None = None,
            cmd: str = 'l',
            have_end_statement: bool = False,
            negate: bool = False,
            strict: bool = False,
    ) -> None:
        super().__init__()

        self.delim = None
        self.odelim = ' '
        self.negate = negate
        self.pattern = None if pattern is None else re.compile(pattern)
        self.cmd = cmd
        self.strict = strict
        self._compile(have_end_statement)

    @classmethod
    def from_options(cls, options: ta.Any, arg: str) -> 'Action':
        negate, pattern, cmd = Action._parse_command(arg)
        return cls(
            pattern=pattern,
            cmd=cmd,
            have_end_statement=(options.end is not None),
            negate=negate,
            strict=options.strict,
        )

    def _compile(self, have_end_statement: bool) -> None:
        if not self.cmd:
            if have_end_statement:
                self.cmd = 't += line'
            else:
                self.cmd = 'l'
        self._codeobj = compile_command(self.cmd)

    def apply(self, context: 'Context', line: str) -> ta.Any:
        """
        Apply action to line.

        :return: Line text or None.
        """

        match = self._match(line)
        if match is None:
            return None
        context['m'] = match
        try:
            return eval_in_context(self._codeobj, context)
        except Exception:  # noqa
            if not self.strict:
                return None
            raise

    def _match(self, line: str) -> ta.Any:
        if self.pattern is None:
            return self.negate
        match = self.pattern.search(line)
        if match is not None:
            return None if self.negate else match.groups()
        elif self.negate:
            return ()
        else:
            return None

    @staticmethod
    def _parse_command(arg: str) -> tuple[bool, str | None, str]:
        match = re.match(r'(?ms)(?:(!)?/((?:\\.|[^/])+)/)?(.*)', arg)
        negate, pattern, cmd = check.not_none(match).groups()
        cmd = cmd.strip()
        negate = bool(negate)
        return negate, pattern, cmd


class Context(dict):
    def apply(
            self,
            numz: int,
            line: str,
            headers: ta.Sequence[str] | None = None,
    ) -> None:
        l = line.rstrip()
        f = l.split(self.delim)
        self.update(line=line, l=l, n=numz + 1, f=f, nf=len(f))
        if headers:
            self.update(itertools.zip_longest(headers, f))

    delim: str | None
    odelim: str
    line_separator: str

    @classmethod
    def from_options(
            cls,
            options: ta.Any,
            modules: ta.Sequence[str],
    ) -> 'Context':
        self = cls()
        self['t'] = ''
        self['m'] = ()
        if options.imports:
            for imp in options.imports.split(','):
                mod = __import__(imp.strip(), fromlist=['.'])
                self.update((k, v) for k, v in inspect.getmembers(mod) if k[0] != '_')

        self.delim = codecs.decode(options.delim, STRING_ESCAPE) if options.delim else None
        self.odelim = codecs.decode(options.delim_out, STRING_ESCAPE)
        self.line_separator = codecs.decode(options.line_separator, STRING_ESCAPE)

        for m in modules:
            try:
                key = m.split('.')[0]
                self[key] = __import__(m)
            except Exception:  # noqa
                pass
        return self


def process(
        context: Context,
        input: ta.TextIO,  # noqa
        output: ta.TextIO,
        begin_statement: str | None,
        actions: ta.Sequence[Action],
        end_statement: str | None,
        strict: bool,
        header: bool,
):
    """Process a stream."""

    # Override "print"
    old_stdout = sys.stdout
    sys.stdout = output
    write = output.write

    def write_result(result, when_true=None):
        if result is True:
            result = when_true
        elif isinstance(result, (list, tuple)):
            result = context.odelim.join(map(str, result))

        if result is not None and result is not False:
            result = str(result)
            if not result.endswith(context.line_separator):
                result = result.rstrip('\n') + context.line_separator
            write(result)

    try:
        headers = None
        if header:
            line = input.readline()
            context.apply(-1, line)
            headers = context['f']

        if begin_statement:
            write_result(eval_in_context(compile_command(begin_statement), context))

        for numz, line in enumerate(input):
            context.apply(numz, line, headers=headers)
            for action in actions:
                write_result(action.apply(context, line), when_true=line)

        if end_statement:
            write_result(eval_in_context(compile_command(end_statement), context))

    finally:
        sys.stdout = old_stdout


def parse_commandline(argv: ta.Sequence[str]) -> tuple[ta.Any, ta.Sequence[str]]:
    parser = argparse.ArgumentParser()
    # parser.set_usage(__doc__.strip())
    parser.add_argument(
        '-I',
        '--in_place',
        dest='in_place',
        help='modify given input file in-place',
        metavar='<filename>',
    )
    parser.add_argument(
        '-i',
        '--import',
        dest='imports',
        help='comma-separated list of modules to "from x import *" from',
        metavar='<modules>',
    )
    parser.add_argument(
        '-F',
        dest='delim',
        help='input delimiter',
        metavar='<delim>',
        default=None,
    )
    parser.add_argument(
        '-O',
        dest='delim_out',
        help='output delimiter',
        metavar='<delim>',
        default=' ',
    )
    parser.add_argument(
        '-L',
        dest='line_separator',
        help='output line separator',
        metavar='<delim>',
        default='\n',
    )
    parser.add_argument(
        '-B',
        '--begin',
        help='begin statement',
        metavar='<statement>',
    )
    parser.add_argument(
        '-E',
        '--end',
        help='end statement',
        metavar='<statement>',
    )
    parser.add_argument(
        '-s',
        '--statement',
        action='store_true',
        help='DEPRECATED. retained for backward compatibility',
    )
    parser.add_argument(
        '-H',
        '--header',
        action='store_true',
        help='use first row as field variable names in subsequent rows',
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='abort on exceptions',
    )
    return parser.parse_known_args(argv[1:])


# For integration tests.
def run(
        argv: ta.Sequence[str],
        input: ta.TextIO,  # noqa
        output: ta.TextIO,
) -> None:
    options, args = parse_commandline(argv)

    with contextlib.ExitStack() as es:
        if options.in_place:
            os.rename(options.in_place, options.in_place + '~')
            input = es.enter_context(open(options.in_place + '~'))  # noqa
            output = es.enter_context(open(options.in_place, 'w'))

        # Auto-import. This is not smart.
        all_text = ' '.join([(options.begin or ''), ' '.join(args), (options.end or '')])
        modules = re.findall(r'([\w.]+)+(?=\.\w+)\b', all_text)

        context = Context.from_options(options, modules)
        actions = [Action.from_options(options, arg) for arg in args]
        if not actions:
            actions = [Action.from_options(options, '')]

        process(
            context,
            input,
            output,
            options.begin,
            actions,
            options.end,
            options.strict,
            options.header,
        )


def main() -> None:
    try:
        run(sys.argv, sys.stdin, sys.stdout)
    except OSError as e:
        # Workaround for close failed in file object destructor: sys.excepthook is missing lost sys.stderr
        # http://stackoverflow.com/questions/7955138/addressing-sys-excepthook-error-in-bash-script
        sys.stderr.write(str(e) + '\n')
        raise SystemExit(1) from None
    except KeyboardInterrupt:
        raise SystemExit(1) from None


# @omlish-manifest
_CLI_MODULE = CliModule('pawk', __name__)


if __name__ == '__main__':
    main()
