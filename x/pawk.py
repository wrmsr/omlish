#!/usr/bin/env python
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
"""
# PAWK - A Python line processor (like AWK)

PAWK aims to bring the full power of Python to AWK-like line-processing.

Here are some quick examples to show some of the advantages of pawk over AWK.

The first example transforms `/etc/hosts` into a JSON map of host to IP:

	cat /etc/hosts | pawk -B 'd={}' -E 'json.dumps(d)' '!/^#/ d[f[1]] = f[0]'

Breaking this down:

1. `-B 'd={}'` is a begin statement initializing a dictionary, executed once before processing begins.
2. `-E 'json.dumps(d)'` is an end statement expression, producing the JSON representation of the dictionary `d`.
3. `!/^#/` tells pawk to match any line *not* beginning with `#`.
4. `d[f[1]] = f[0]` adds a dictionary entry where the key is the second field in the line (the first hostname) and the value is the first field (the IP address).

And another example showing how to bzip2-compress + base64-encode a file:

	cat pawk.py | pawk -E 'base64.encodestring(bz2.compress(t))'

### AWK example translations

Most basic AWK constructs are available. You can find more idiomatic examples below in the example section, but here are a bunch of awk commands and their equivalent pawk commands to get started with:

Print lines matching a pattern:

	ls -l / | awk '/etc/'
	ls -l / | pawk '/etc/'

Print lines *not* matching a pattern:

	ls -l / | awk '!/etc/'
	ls -l / | pawk '!/etc/'

Field slicing and dicing (here pawk wins because of Python's array slicing):

	ls -l / | awk '/etc/ {print $5, $6, $7, $8, $9}'
	ls -l / | pawk '/etc/ f[4:]'

Begin and end end actions (in this case, summing the sizes of all files):

	ls -l | awk 'BEGIN {c = 0} {c += $5} END {print c}'
	ls -l | pawk -B 'c = 0' -E 'c' 'c += int(f[4])'

Print files where a field matches a numeric expression (in this case where files are > 1024 bytes):

	ls -l | awk '$5 > 1024'
	ls -l | pawk 'int(f[4]) > 1024'

Matching a single field (any filename with "t" in it):

	ls -l | awk '$NF ~/t/'
	ls -l | pawk '"t" in f[-1]'

## Installation

It should be as simple as:

```
pip install pawk
```

But if that doesn't work, just download the `pawk.py`, make it executable, and place it somewhere in your path.

## Expression evaluation

PAWK evaluates a Python expression or statement against each line in stdin. The following variables are available in local context:

- `line` - Current line text, including newline.
- `l` - Current line text, excluding newline.
- `n` - The current 1-based line number.
- `f` - Fields of the line (split by the field separator `-F`).
- `nf` - Number of fields in this line.
- `m` - Tuple of match regular expression capture groups, if any.


In the context of the `-E` block:

- `t` - The entire input text up to the current cursor position.

If the flag `-H, --header` is provided, each field in the first row of the input will be treated as field variable names in subsequent rows. The header is not output. For example, given the input:

```
count name
12 bob
34 fred
```

We could do:

```
$ pawk -H '"%s is %s" % (name, count)' < input.txt
bob is 12
fred is 34
```

To output a header as well, use `-B`:

```
$ pawk -H -B '"name is count"' '"%s is %s" % (name, count)' < input.txt
name is count
bob is 12
fred is 34
```

Module references will be automatically imported if possible. Additionally, the `--import <module>[,<module>,...]` flag can be used to import symbols from a set of modules into the evaluation context.

eg. `--import os.path` will import all symbols from `os.path`, such as `os.path.isfile()`, into the context.

## Output

### Line actions

The type of the evaluated expression determines how output is displayed:

- `tuple` or `list`: the elements are converted to strings and joined with the output delimiter (`-O`).
- `None` or `False`: nothing is output for that line.
- `True`: the original line is output.
- Any other value is converted to a string.

### Start/end blocks

The rules are the same as for line actions with one difference.  Because there is no "line" that corresponds to them, an expression returning True is ignored.

	$ echo -ne 'foo\nbar' | pawk -E t
    foo
    bar


## Command-line usage

```
Usage: cat input | pawk [<options>] <expr>

A Python line-processor (like awk).

See https://github.com/alecthomas/pawk for details. Based on
http://code.activestate.com/recipes/437932/.

Options:
  -h, --help            show this help message and exit
  -I <filename>, --in_place=<filename>
                        modify given input file in-place
  -i <modules>, --import=<modules>
                        comma-separated list of modules to "from x import *"
                        from
  -F <delim>            input delimiter
  -O <delim>            output delimiter
  -L <delim>            output line separator
  -B <statement>, --begin=<statement>
                        begin statement
  -E <statement>, --end=<statement>
                        end statement
  -s, --statement       DEPRECATED. retained for backward compatibility
  -H, --header          use first row as field variable names in subsequent
                        rows
  --strict              abort on exceptions
```

## Examples

### Line processing

Print the name and size of every file from stdin:

	find . -type f | pawk 'f[0], os.stat(f[0]).st_size'

> **Note:** this example also shows how pawk automatically imports referenced modules, in this case `os`.

Print the sum size of all files from stdin:

	find . -type f | \
		pawk \
			--begin 'c=0' \
			--end c \
			'c += os.stat(f[0]).st_size'

Short-flag version:

	find . -type f | pawk -B c=0 -E c 'c += os.stat(f[0]).st_size'


### Whole-file processing

If you do not provide a line expression, but do provide an end statement, pawk will accumulate each line, and the entire file's text will be available in the end statement as `t`. This is useful for operations on entire files, like the following example of converting a file from markdown to HTML:

	cat README.md | \
		pawk --end 'markdown.markdown(t)'

Short-flag version:

	cat README.md | pawk -E 'markdown.markdown(t)'
"""
import ast
import codecs
import inspect
import optparse
import os
import re
import sys


__version__ = '0.8.0'

RESULT_VAR_NAME = "__result"

if sys.version_info[0] > 2:
    from itertools import zip_longest

    try:
        exec_ = __builtins__['exec']
    except TypeError:
        exec_ = getattr(__builtins__, 'exec')
    STRING_ESCAPE = 'unicode_escape'
else:
    from itertools import izip_longest as zip_longest


    def exec_(_code_, _globs_=None, _locs_=None):
        if _globs_ is None:
            frame = sys._getframe(1)
            _globs_ = frame.f_globals
            if _locs_ is None:
                _locs_ = frame.f_locals
            del frame
        elif _locs_ is None:
            _locs_ = _globs_
        exec("""exec _code_ in _globs_, _locs_""")


    STRING_ESCAPE = 'string_escape'


# Store the last expression, if present, into variable var_name.
def save_last_expression(tree, var_name=RESULT_VAR_NAME):
    body = tree.body
    node = body[-1] if len(body) else None
    body.insert(0, ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())],
                              value=ast.Constant(None)))
    if node and isinstance(node, ast.Expr):
        body[-1] = ast.copy_location(ast.Assign(
            targets=[ast.Name(id=var_name, ctx=ast.Store())], value=node.value), node)
    return ast.fix_missing_locations(tree)


def compile_command(text):
    tree = save_last_expression(compile(text, 'EXPR', 'exec', flags=ast.PyCF_ONLY_AST))
    return compile(tree, 'EXPR', 'exec')


def eval_in_context(codeobj, context, var_name=RESULT_VAR_NAME):
    exec_(codeobj, globals(), context)
    return context.pop(var_name, None)


class Action(object):
    """Represents a single action to be applied to each line."""

    def __init__(self, pattern=None, cmd='l', have_end_statement=False, negate=False, strict=False):
        self.delim = None
        self.odelim = ' '
        self.negate = negate
        self.pattern = None if pattern is None else re.compile(pattern)
        self.cmd = cmd
        self.strict = strict
        self._compile(have_end_statement)

    @classmethod
    def from_options(cls, options, arg):
        negate, pattern, cmd = Action._parse_command(arg)
        return cls(pattern=pattern, cmd=cmd, have_end_statement=(options.end is not None), negate=negate,
                   strict=options.strict)

    def _compile(self, have_end_statement):
        if not self.cmd:
            if have_end_statement:
                self.cmd = 't += line'
            else:
                self.cmd = 'l'
        self._codeobj = compile_command(self.cmd)

    def apply(self, context, line):
        """Apply action to line.

        :return: Line text or None.
        """
        match = self._match(line)
        if match is None:
            return None
        context['m'] = match
        try:
            return eval_in_context(self._codeobj, context)
        except:
            if not self.strict:
                return None
            raise

    def _match(self, line):
        if self.pattern is None:
            return self.negate
        match = self.pattern.search(line)
        if match is not None:
            return None if self.negate else match.groups()
        elif self.negate:
            return ()

    @staticmethod
    def _parse_command(arg):
        match = re.match(r'(?ms)(?:(!)?/((?:\\.|[^/])+)/)?(.*)', arg)
        negate, pattern, cmd = match.groups()
        cmd = cmd.strip()
        negate = bool(negate)
        return negate, pattern, cmd


class Context(dict):
    def apply(self, numz, line, headers=None):
        l = line.rstrip()
        f = l.split(self.delim)
        self.update(line=line, l=l, n=numz + 1, f=f, nf=len(f))
        if headers:
            self.update(zip_longest(headers, f))

    @classmethod
    def from_options(cls, options, modules):
        self = cls()
        self['t'] = ''
        self['m'] = ()
        if options.imports:
            for imp in options.imports.split(','):
                m = __import__(imp.strip(), fromlist=['.'])
                self.update((k, v) for k, v in inspect.getmembers(m) if k[0] != '_')

        self.delim = codecs.decode(options.delim, STRING_ESCAPE) if options.delim else None
        self.odelim = codecs.decode(options.delim_out, STRING_ESCAPE)
        self.line_separator = codecs.decode(options.line_separator, STRING_ESCAPE)

        for m in modules:
            try:
                key = m.split('.')[0]
                self[key] = __import__(m)
            except:
                pass
        return self


def process(context, input, output, begin_statement, actions, end_statement, strict, header):
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


def parse_commandline(argv):
    parser = optparse.OptionParser(version=__version__)
    parser.set_usage(__doc__.strip())
    parser.add_option('-I', '--in_place', dest='in_place', help='modify given input file in-place', metavar='<filename>')
    parser.add_option('-i', '--import', dest='imports', help='comma-separated list of modules to "from x import *" from', metavar='<modules>')
    parser.add_option('-F', dest='delim', help='input delimiter', metavar='<delim>', default=None)
    parser.add_option('-O', dest='delim_out', help='output delimiter', metavar='<delim>', default=' ')
    parser.add_option('-L', dest='line_separator', help='output line separator', metavar='<delim>', default='\n')
    parser.add_option('-B', '--begin', help='begin statement', metavar='<statement>')
    parser.add_option('-E', '--end', help='end statement', metavar='<statement>')
    parser.add_option('-s', '--statement', action='store_true', help='DEPRECATED. retained for backward compatibility')
    parser.add_option('-H', '--header', action='store_true', help='use first row as field variable names in subsequent rows')
    parser.add_option('--strict', action='store_true', help='abort on exceptions')
    return parser.parse_args(argv[1:])


# For integration tests.
def run(argv, input, output):
    options, args = parse_commandline(argv)

    try:
        if options.in_place:
            os.rename(options.in_place, options.in_place + '~')
            input = open(options.in_place + '~')
            output = open(options.in_place, 'w')

        # Auto-import. This is not smart.
        all_text = ' '.join([(options.begin or ''), ' '.join(args), (options.end or '')])
        modules = re.findall(r'([\w.]+)+(?=\.\w+)\b', all_text)

        context = Context.from_options(options, modules)
        actions = [Action.from_options(options, arg) for arg in args]
        if not actions:
            actions = [Action.from_options(options, '')]

        process(context, input, output, options.begin, actions, options.end, options.strict, options.header)
    finally:
        if options.in_place:
            output.close()
            input.close()


def main():
    try:
        run(sys.argv, sys.stdin, sys.stdout)
    except EnvironmentError as e:
        # Workaround for close failed in file object destructor: sys.excepthook is missing lost sys.stderr
        # http://stackoverflow.com/questions/7955138/addressing-sys-excepthook-error-in-bash-script
        sys.stderr.write(str(e) + '\n')
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(1)


if __name__ == '__main__':
    main()


"""

TEST_INPUT_LS = r'''
total 72
-rw-r-----  1 alec  staff    18 Feb  9 11:52 MANIFEST.in
-rw-r-----@ 1 alec  staff  3491 Feb 10 11:08 README.md
drwxr-x---  4 alec  staff   136 Feb  9 23:35 dist/
-rwxr-x---  1 alec  staff    53 Feb 10 04:47 pawk*
drwxr-x---  6 alec  staff   204 Feb  9 21:09 pawk.egg-info/
-rw-r-----  1 alec  staff  5045 Feb 10 11:37 pawk.py
-rw-r--r--  1 alec  staff   521 Feb 10 04:56 pawk_test.py
-rw-r-----  1 alec  staff   468 Feb 10 04:42 setup.py
'''

TEST_INPUT_CSV_WITH_EMPTY_FIELD = r'''
model,color,price
A01,,100
B03,blue,200
'''

def run_integration_test(input, args):
    input = StringIO(input.strip())
    output = StringIO()
    run(['pawk'] + args, input, output)
    return output.getvalue().strip()


def test_action_parse():
    negate, pattern, cmd = Action()._parse_command(r'/(\w+)/ l')
    assert pattern == r'(\w+)'
    assert cmd == 'l'
    assert negate is False


def test_action_match():
    action = Action(r'(\w+) \w+')
    groups = action._match('test case')
    assert groups == ('test',)


def test_action_match_negate():
    action = Action(r'(\w+) \w+', negate=True)
    groups = action._match('test case')
    assert groups is None
    groups = action._match('test')
    assert groups == ()


def test_integration_sum():
    out = run_integration_test(TEST_INPUT_LS, ['-Bc = 0', '-Ec', 'c += int(f[4])'])
    assert out == '9936'


def test_integration_match():
    out = run_integration_test(TEST_INPUT_LS, ['/pawk_test/ f[4]'])
    assert out == '521'


def test_integration_negate_match():
    out = run_integration_test(TEST_INPUT_LS, ['!/^total|pawk/ f[-1]'])
    assert out.splitlines() == ['MANIFEST.in', 'README.md', 'dist/', 'setup.py']


def test_integration_truth():
    out = run_integration_test(TEST_INPUT_LS, ['int(f[4]) > 1024'])
    assert [r.split()[-1] for r in out.splitlines()] == ['README.md', 'pawk.py']


def test_integration_multiple_actions():
    out = run_integration_test(TEST_INPUT_LS, ['/setup/', '/README/'])
    assert [r.split()[-1] for r in out.splitlines()] == ['README.md', 'setup.py']


def test_integration_csv_empty_fields():
    out = run_integration_test(TEST_INPUT_CSV_WITH_EMPTY_FIELD, ['-F,', 'f[2]'])
    assert out.splitlines() == ['price', '100', '200']
    out = run_integration_test(TEST_INPUT_CSV_WITH_EMPTY_FIELD, ['-F,', 'f[1]'])
    assert out.splitlines() == ['color', '', 'blue']
"""
