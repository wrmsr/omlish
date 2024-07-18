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
"""
Find intermediate evalutation results in assert statements through builtin AST. This should replace _assertionold.py
eventually.
"""
import ast
import bisect
import builtins
import errno
import inspect
import linecache
import os.path
import reprlib
import sys
import tokenize


_sysex = (KeyboardInterrupt, SystemExit, MemoryError, GeneratorExit)


##


class SafeRepr(reprlib.Repr):
    """
    subclass of repr.Repr that limits the resulting size of repr() and includes information on exceptions raised during
    the call.
    """

    def repr(self, x):
        return self._callhelper(reprlib.Repr.repr, self, x)

    def repr_unicode(self, x, level):
        # Strictly speaking wrong on narrow builds
        def repr(u):
            if "'" not in u:
                return "'%s'" % u
            elif '"' not in u:
                return '"%s"' % u
            else:
                return "'%s'" % u.replace("'", r"\'")

        s = repr(x[:self.maxstring])
        if len(s) > self.maxstring:
            i = max(0, (self.maxstring - 3) // 2)
            j = max(0, self.maxstring - 3 - i)
            s = repr(x[:i] + x[len(x) - j:])
            s = s[:i] + '...' + s[len(s) - j:]
        return s

    def repr_instance(self, x, level):
        return self._callhelper(repr, x)

    def _callhelper(self, call, x, *args):
        try:
            # Try the vanilla repr and make sure that the result is a string
            s = call(x, *args)
        except _sysex:
            raise
        except:
            cls, e, tb = sys.exc_info()
            exc_name = getattr(cls, '__name__', 'unknown')
            try:
                exc_info = str(e)
            except _sysex:
                raise
            except:
                exc_info = 'unknown'
            return '<[%s("%s") raised in repr()] %s object at 0x%x>' % (
                exc_name, exc_info, x.__class__.__name__, id(x))
        else:
            if len(s) > self.maxsize:
                i = max(0, (self.maxsize - 3) // 2)
                j = max(0, self.maxsize - 3 - i)
                s = s[:i] + '...' + s[len(s) - j:]
            return s


def saferepr(obj, maxsize=240):
    """
    return a size-limited safe repr-string for the given object. Failing __repr__ functions of user instances will be
    represented with a short exception info and 'saferepr' generally takes care to never raise exceptions itself.  This
    function is a wrapper around the Repr/reprlib functionality of the standard 2.6 lib.
    """
    # review exception handling
    srepr = SafeRepr()
    srepr.maxstring = maxsize
    srepr.maxsize = maxsize
    srepr.maxother = 160
    return srepr.repr(obj)


##


def findsource(obj):
    try:
        sourcelines, lineno = inspect.findsource(obj)
    except _sysex:
        raise
    except:
        return None, -1
    source = Source()
    source.lines = [line.rstrip() for line in sourcelines]
    return source, lineno


def getsource(obj, **kwargs):
    obj = getrawcode(obj)
    try:
        strsrc = inspect.getsource(obj)
    except IndentationError:
        strsrc = "\"Buggy python version consider upgrading, cannot get source\""
    assert isinstance(strsrc, str)
    return Source(strsrc, **kwargs)


def deindent(lines, offset=None):
    if offset is None:
        for line in lines:
            line = line.expandtabs()
            s = line.lstrip()
            if s:
                offset = len(line) - len(s)
                break
        else:
            offset = 0
    if offset == 0:
        return list(lines)
    newlines = []

    def readline_generator(lines):
        for line in lines:
            yield line + '\n'
        while True:
            yield ''

    it = readline_generator(lines)

    try:
        for _, _, (sline, _), (eline, _), _ in tokenize.generate_tokens(lambda: next(it)):
            if sline > len(lines):
                break  # End of input reached
            if sline > len(newlines):
                line = lines[sline - 1].expandtabs()
                if line.lstrip() and line[:offset].isspace():
                    line = line[offset:]  # Deindent
                newlines.append(line)

            for i in range(sline, eline):
                # Don't deindent continuing lines of multiline tokens (i.e. multiline strings)
                newlines.append(lines[i])
    except (IndentationError, tokenize.TokenError):
        pass
    # Add any lines we didn't see. E.g. if an exception was raised.
    newlines.extend(lines[len(newlines):])
    return newlines


def get_statement_startend2(lineno, node):
    import ast
    # flatten all statements and except handlers into one lineno-list AST's line numbers start indexing at 1
    l = []
    for x in ast.walk(node):
        if isinstance(x, ast.stmt) or isinstance(x, ast.ExceptHandler):
            l.append(x.lineno - 1)
            for name in "finalbody", "orelse":
                val = getattr(x, name, None)
                if val:
                    # treat the finally/orelse part as its own statement
                    l.append(val[0].lineno - 1 - 1)
    l.sort()
    insert_index = bisect.bisect_right(l, lineno)
    start = l[insert_index - 1]
    if insert_index >= len(l):
        end = None
    else:
        end = l[insert_index]
    return start, end


def getstatementrange_ast(lineno, source, assertion=False, astnode=None):
    if astnode is None:
        content = str(source)
        astnode = compile(content, "source", "exec", 1024)  # 1024 for AST
    start, end = get_statement_startend2(lineno, astnode)
    # we need to correct the end:
    # - ast-parsing strips comments
    # - there might be empty lines
    # - we might have lesser indented code blocks at the end
    if end is None:
        end = len(source.lines)

    if end > start + 1:
        # make sure we don't span differently indented code blocks
        # by using the BlockFinder helper used which inspect.getsource() uses itself
        block_finder = inspect.BlockFinder()
        # if we start with an indented line, put blockfinder to "started" mode
        block_finder.started = source.lines[start][0].isspace()
        it = ((x + "\n") for x in source.lines[start:end])
        try:
            for tok in tokenize.generate_tokens(lambda: next(it)):
                block_finder.tokeneater(*tok)
        except (inspect.EndOfBlock, IndentationError):
            end = block_finder.last + start
        except Exception:
            pass

    # the end might still point to a comment or empty line, correct it
    while end:
        line = source.lines[end - 1].lstrip()
        if line.startswith("#") or not line:
            end -= 1
        else:
            break
    return astnode, start, end


class Source:
    """a immutable object holding a source code fragment, possibly deindenting it."""
    _compilecounter = 0

    def __init__(self, *parts, **kwargs):
        self.lines = lines = []
        de = kwargs.get('deindent', True)
        rstrip = kwargs.get('rstrip', True)
        for part in parts:
            if not part:
                partlines = []
            if isinstance(part, Source):
                partlines = part.lines
            elif isinstance(part, (tuple, list)):
                partlines = [x.rstrip("\n") for x in part]
            elif isinstance(part, str):
                partlines = part.split('\n')
                if rstrip:
                    while partlines:
                        if partlines[-1].strip():
                            break
                        partlines.pop()
            else:
                partlines = getsource(part, deindent=de).lines
            if de:
                partlines = deindent(partlines)
            lines.extend(partlines)

    def __eq__(self, other):
        try:
            return self.lines == other.lines
        except AttributeError:
            if isinstance(other, str):
                return str(self) == other
            return False

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.lines[key]
        else:
            if key.step not in (None, 1):
                raise IndexError("cannot slice a Source with a step")
            return self.__getslice__(key.start, key.stop)

    def __len__(self):
        return len(self.lines)

    def __getslice__(self, start, end):
        newsource = Source()
        newsource.lines = self.lines[start:end]
        return newsource

    def strip(self):
        """return new source object with trailing and leading blank lines removed."""
        start, end = 0, len(self)
        while start < end and not self.lines[start].strip():
            start += 1
        while end > start and not self.lines[end - 1].strip():
            end -= 1
        source = Source()
        source.lines[:] = self.lines[start:end]
        return source

    def putaround(self, before='', after='', indent=' ' * 4):
        """return a copy of the source object with 'before' and 'after' wrapped around it."""
        before = Source(before)
        after = Source(after)
        newsource = Source()
        lines = [(indent + line) for line in self.lines]
        newsource.lines = before.lines + lines + after.lines
        return newsource

    def indent(self, indent=' ' * 4):
        """return a copy of the source object with all lines indented by the given indent-string."""
        newsource = Source()
        newsource.lines = [(indent + line) for line in self.lines]
        return newsource

    def getstatement(self, lineno, assertion=False):
        """return Source statement which contains the given linenumber (counted from 0)."""
        start, end = self.getstatementrange(lineno, assertion)
        return self[start:end]

    def getstatementrange(self, lineno, assertion=False):
        """return (start, end) tuple which spans the minimal statement region which containing the given lineno."""
        if not (0 <= lineno < len(self)):
            raise IndexError("lineno out of range")
        ast, start, end = getstatementrange_ast(lineno, self)
        return start, end

    def deindent(self, offset=None):
        """
        return a new source object deindented by offset. If offset is None then guess an indentation offset from the
        first non-blank line.  Subsequent lines which have a lower indentation offset will be copied verbatim as they
        are assumed to be part of multilines.
        """
        # XXX maybe use the tokenizer to properly handle multiline strings etc.pp?
        newsource = Source()
        newsource.lines[:] = deindent(self.lines, offset)
        return newsource

    def isparseable(self, deindent=True):
        """return True if source is parseable, heuristically deindenting it by default."""
        try:
            import parser
        except ImportError:
            syntax_checker = lambda x: compile(x, 'asd', 'exec')
        else:
            syntax_checker = parser.suite

        if deindent:
            source = str(self.deindent())
        else:
            source = str(self)
        try:
            # compile(source+'\n', "x", "exec")
            syntax_checker(source + '\n')
        except KeyboardInterrupt:
            raise
        except Exception:
            return False
        else:
            return True

    def __str__(self):
        return "\n".join(self.lines)

    def compile(self, filename=None, mode='exec', flag=0, dont_inherit=0, _genframe=None):
        """
        return compiled code object. if filename is None invent an artificial filename which displays the source/line
        position of the caller frame.
        """
        if not filename or not os.path.isfile(filename):
            if _genframe is None:
                _genframe = sys._getframe(1)  # the caller
            fn, lineno = _genframe.f_code.co_filename, _genframe.f_lineno
            base = "<%d-codegen " % self._compilecounter
            self.__class__._compilecounter += 1
            if not filename:
                filename = base + '%s:%d>' % (fn, lineno)
            else:
                filename = base + '%r %s:%d>' % (filename, fn, lineno)
        source = "\n".join(self.lines) + '\n'
        try:
            co = compile(source, filename, mode, flag)
        except SyntaxError:
            ex = sys.exc_info()[1]
            # re-represent syntax errors from parsing python strings
            msglines = self.lines[:ex.lineno]
            if ex.offset:
                msglines.append(" " * ex.offset + '^')
            msglines.append("(code was compiled probably from here: %s)" % filename)
            newex = SyntaxError('\n'.join(msglines))
            newex.offset = ex.offset
            newex.lineno = ex.lineno
            newex.text = ex.text
            raise newex
        else:
            if flag & ast.PyCF_ONLY_AST:
                return co
            lines = [(x + "\n") for x in self.lines]
            linecache.cache[filename] = (1, None, lines, filename)
            return co


##


def getrawcode(obj, trycall=True):
    """ return code object for given function. """
    try:
        return obj.__code__
    except AttributeError:
        obj = getattr(obj, 'im_func', obj)
        obj = getattr(obj, 'func_code', obj)
        obj = getattr(obj, 'f_code', obj)
        obj = getattr(obj, '__code__', obj)
        if trycall and not hasattr(obj, 'co_firstlineno'):
            if hasattr(obj, '__call__') and not inspect.isclass(obj):
                x = getrawcode(obj.__call__, trycall=False)
                if hasattr(x, 'co_firstlineno'):
                    return x
        return obj


class Code:
    """ wrapper around Python code objects """

    def __init__(self, rawcode):
        if not hasattr(rawcode, "co_filename"):
            rawcode = getrawcode(rawcode)
        try:
            self.filename = rawcode.co_filename
            self.firstlineno = rawcode.co_firstlineno - 1
            self.name = rawcode.co_name
        except AttributeError:
            raise TypeError("not a code object: %r" % (rawcode,))
        self.raw = rawcode

    def __eq__(self, other):
        return self.raw == other.raw

    def __ne__(self, other):
        return not self == other

    @property
    def fullsource(self):
        """return a py.code.Source object for the full source file of the code"""
        full, _ = findsource(self.raw)
        return full

    def source(self):
        """return a py.code.Source object for the code object's source only"""
        # return source only for that part of code
        return Source(self.raw)

    def getargs(self, var=False):
        """
        return a tuple with the argument names for the code object

        if 'var' is set True also return the names of the variable and keyword arguments when present
        """
        # handfull shortcut for getting args
        raw = self.raw
        argcount = raw.co_argcount
        if var:
            argcount += raw.co_flags & inspect.CO_VARARGS
            argcount += raw.co_flags & inspect.CO_VARKEYWORDS
        return raw.co_varnames[:argcount]


class Frame:
    """Wrapper around a Python frame holding f_locals and f_globals in which expressions can be evaluated."""
    def __init__(self, frame):
        self.lineno = frame.f_lineno - 1
        self.f_globals = frame.f_globals
        self.f_locals = frame.f_locals
        self.raw = frame
        self.code = Code(frame.f_code)

    @property
    def statement(self):
        """ statement this frame is at """
        if self.code.fullsource is None:
            return Source("")
        return self.code.fullsource.getstatement(self.lineno)

    def eval(self, code, **vars):
        """
        evaluate 'code' in the frame. 'vars' are optional additional local variables. returns the result of the
        evaluation.
        """
        f_locals = self.f_locals.copy()
        f_locals.update(vars)
        return eval(code, self.f_globals, f_locals)

    def exec_(self, code, **vars):
        """exec 'code' in the frame. 'vars' are optiona; additional local variables"""
        f_locals = self.f_locals.copy()
        f_locals.update(vars)
        exec(code, self.f_globals, f_locals)

    def repr(self, object):
        """return a 'safe' (non-recursive, one-line) string repr for 'object'"""
        return saferepr(object)

    def is_true(self, object):
        return object

    def getargs(self, var=False):
        """
        return a list of tuples (name, value) for all arguments. if 'var' is set True also include the variable and
        keyword arguments when present
        """
        retval = []
        for arg in self.code.getargs(var):
            try:
                retval.append((arg, self.f_locals[arg]))
            except KeyError:
                pass  # this can occur when using Psyco
        return retval


##


_reprcompare = None  # if set, will be called by assert reinterp for comparison ops


def _format_explanation(explanation):
    """This formats an explanation

    Normally all embedded newlines are escaped, however there are three exceptions: \n{, \n} and \n~.  The first two are
    intended cover nested explanations, see function and attribute explanations for examples (.visit_Call(),
    visit_Attribute()).  The last one is for when one explanation needs to span multiple lines, e.g. when displaying
    diffs.
    """
    raw_lines = (explanation or '').split('\n')
    # escape newlines not followed by {, } and ~
    lines = [raw_lines[0]]
    for l in raw_lines[1:]:
        if l.startswith('{') or l.startswith('}') or l.startswith('~'):
            lines.append(l)
        else:
            lines[-1] += '\\n' + l

    result = lines[:1]
    stack = [0]
    stackcnt = [0]
    for line in lines[1:]:
        if line.startswith('{'):
            if stackcnt[-1]:
                s = 'and   '
            else:
                s = 'where '
            stack.append(len(result))
            stackcnt[-1] += 1
            stackcnt.append(0)
            result.append(' +' + '  ' * (len(stack) - 1) + s + line[1:])
        elif line.startswith('}'):
            assert line.startswith('}')
            stack.pop()
            stackcnt.pop()
            result[stack[-1]] += line[1:]
        else:
            assert line.startswith('~')
            result.append('  ' * len(stack) + line[1:])
    assert len(stack) == 1
    return '\n'.join(result)


class AssertionError(builtins.AssertionError):
    def __init__(self, *args):
        super().__init__(self, *args)
        if args:
            try:
                self.msg = str(args[0])
            except _sysex:
                raise
            except:
                self.msg = "<[broken __repr__] %s at %0xd>" % (
                    args[0].__class__, id(args[0]))
        else:
            f = Frame(sys._getframe(1))
            try:
                source = f.code.fullsource
                if source is not None:
                    try:
                        source = source.getstatement(f.lineno, assertion=True)
                    except IndexError:
                        source = None
                    else:
                        source = str(source.deindent()).strip()
            except errno.ENOENT:
                source = None
                # this can also occur during reinterpretation, when the
                # co_filename is set to "<run>".
            if source:
                self.msg = interpret(source, f, should_fail=True)
            else:
                self.msg = "<could not determine information>"
            if not self.args:
                self.args = (self.msg,)


def _is_ast_expr(node):
    return isinstance(node, ast.expr)


def _is_ast_stmt(node):
    return isinstance(node, ast.stmt)


class Failure(Exception):
    """Error found while interpreting AST."""

    def __init__(self, explanation=""):
        self.cause = sys.exc_info()
        self.explanation = explanation


def interpret(source, frame, should_fail=False):
    mod = ast.parse(source)
    visitor = DebugInterpreter(frame)
    try:
        visitor.visit(mod)
    except Failure:
        failure = sys.exc_info()[1]
        return getfailure(failure)
    if should_fail:
        return (
            "(assertion failed, but when it was re-run for printing intermediate values, it did not fail.  "
            "Suggestions: compute assert expression before the assert or use --no-assert)"
        )


def run(offending_line, frame=None):
    if frame is None:
        frame = Frame(sys._getframe(1))
    return interpret(offending_line, frame)


def getfailure(failure):
    explanation = _format_explanation(failure.explanation)
    value = failure.cause[1]
    if str(value):
        lines = explanation.splitlines()
        if not lines:
            lines.append("")
        lines[0] += " << %s" % (value,)
        explanation = "\n".join(lines)
    text = "%s: %s" % (failure.cause[0].__name__, explanation)
    if text.startswith("AssertionError: assert "):
        text = text[16:]
    return text


operator_map = {
    ast.BitOr: "|",
    ast.BitXor: "^",
    ast.BitAnd: "&",
    ast.LShift: "<<",
    ast.RShift: ">>",
    ast.Add: "+",
    ast.Sub: "-",
    ast.Mult: "*",
    ast.Div: "/",
    ast.FloorDiv: "//",
    ast.Mod: "%",
    ast.Eq: "==",
    ast.NotEq: "!=",
    ast.Lt: "<",
    ast.LtE: "<=",
    ast.Gt: ">",
    ast.GtE: ">=",
    ast.Pow: "**",
    ast.Is: "is",
    ast.IsNot: "is not",
    ast.In: "in",
    ast.NotIn: "not in"
}

unary_map = {
    ast.Not: "not %s",
    ast.Invert: "~%s",
    ast.USub: "-%s",
    ast.UAdd: "+%s"
}


class DebugInterpreter(ast.NodeVisitor):
    """Interpret AST nodes to gleam useful debugging information. """

    def __init__(self, frame):
        self.frame = frame

    def generic_visit(self, node):
        # Fallback when we don't have a special implementation.
        if _is_ast_expr(node):
            mod = ast.Expression(node)
            co = self._compile(mod)
            try:
                result = self.frame.eval(co)
            except Exception:
                raise Failure()
            explanation = self.frame.repr(result)
            return explanation, result
        elif _is_ast_stmt(node):
            mod = ast.Module([node])
            co = self._compile(mod, "exec")
            try:
                self.frame.exec_(co)
            except Exception:
                raise Failure()
            return None, None
        else:
            raise AssertionError("can't handle %s" % (node,))

    def _compile(self, source, mode="eval"):
        return compile(source, "<assertion interpretation>", mode)

    def visit_Expr(self, expr):
        return self.visit(expr.value)

    def visit_Module(self, mod):
        for stmt in mod.body:
            self.visit(stmt)

    def visit_Name(self, name):
        explanation, result = self.generic_visit(name)
        # See if the name is local.
        source = "%r in locals() is not globals()" % (name.id,)
        co = self._compile(source)
        try:
            local = self.frame.eval(co)
        except Exception:
            # have to assume it isn't
            local = False
        if not local:
            return name.id, result
        return explanation, result

    def visit_Compare(self, comp):
        left = comp.left
        left_explanation, left_result = self.visit(left)
        for op, next_op in zip(comp.ops, comp.comparators):
            next_explanation, next_result = self.visit(next_op)
            op_symbol = operator_map[op.__class__]
            explanation = "%s %s %s" % (left_explanation, op_symbol,
                                        next_explanation)
            source = "__exprinfo_left %s __exprinfo_right" % (op_symbol,)
            co = self._compile(source)
            try:
                result = self.frame.eval(co, __exprinfo_left=left_result,
                                         __exprinfo_right=next_result)
            except Exception:
                raise Failure(explanation)
            try:
                if not result:
                    break
            except KeyboardInterrupt:
                raise
            except:
                break
            left_explanation, left_result = next_explanation, next_result

        rcomp = _reprcompare
        if rcomp:
            res = rcomp(op_symbol, left_result, next_result)
            if res:
                explanation = res
        return explanation, result

    def visit_BoolOp(self, boolop):
        is_or = isinstance(boolop.op, ast.Or)
        explanations = []
        for operand in boolop.values:
            explanation, result = self.visit(operand)
            explanations.append(explanation)
            if result == is_or:
                break
        name = is_or and " or " or " and "
        explanation = "(" + name.join(explanations) + ")"
        return explanation, result

    def visit_UnaryOp(self, unary):
        pattern = unary_map[unary.op.__class__]
        operand_explanation, operand_result = self.visit(unary.operand)
        explanation = pattern % (operand_explanation,)
        co = self._compile(pattern % ("__exprinfo_expr",))
        try:
            result = self.frame.eval(co, __exprinfo_expr=operand_result)
        except Exception:
            raise Failure(explanation)
        return explanation, result

    def visit_BinOp(self, binop):
        left_explanation, left_result = self.visit(binop.left)
        right_explanation, right_result = self.visit(binop.right)
        symbol = operator_map[binop.op.__class__]
        explanation = "(%s %s %s)" % (left_explanation, symbol,
                                      right_explanation)
        source = "__exprinfo_left %s __exprinfo_right" % (symbol,)
        co = self._compile(source)
        try:
            result = self.frame.eval(co, __exprinfo_left=left_result,
                                     __exprinfo_right=right_result)
        except Exception:
            raise Failure(explanation)
        return explanation, result

    def visit_Call(self, call):
        func_explanation, func = self.visit(call.func)
        arg_explanations = []
        ns = {"__exprinfo_func": func}
        arguments = []
        for arg in call.args:
            arg_explanation, arg_result = self.visit(arg)
            arg_name = "__exprinfo_%s" % (len(ns),)
            ns[arg_name] = arg_result
            arguments.append(arg_name)
            arg_explanations.append(arg_explanation)
        for keyword in call.keywords:
            arg_explanation, arg_result = self.visit(keyword.value)
            arg_name = "__exprinfo_%s" % (len(ns),)
            ns[arg_name] = arg_result
            keyword_source = "%s=%%s" % (keyword.arg)
            arguments.append(keyword_source % (arg_name,))
            arg_explanations.append(keyword_source % (arg_explanation,))
        if call.starargs:
            arg_explanation, arg_result = self.visit(call.starargs)
            arg_name = "__exprinfo_star"
            ns[arg_name] = arg_result
            arguments.append("*%s" % (arg_name,))
            arg_explanations.append("*%s" % (arg_explanation,))
        if call.kwargs:
            arg_explanation, arg_result = self.visit(call.kwargs)
            arg_name = "__exprinfo_kwds"
            ns[arg_name] = arg_result
            arguments.append("**%s" % (arg_name,))
            arg_explanations.append("**%s" % (arg_explanation,))
        args_explained = ", ".join(arg_explanations)
        explanation = "%s(%s)" % (func_explanation, args_explained)
        args = ", ".join(arguments)
        source = "__exprinfo_func(%s)" % (args,)
        co = self._compile(source)
        try:
            result = self.frame.eval(co, **ns)
        except Exception:
            raise Failure(explanation)
        pattern = "%s\n{%s = %s\n}"
        rep = self.frame.repr(result)
        explanation = pattern % (rep, rep, explanation)
        return explanation, result

    def _is_builtin_name(self, name):
        pattern = "%r not in globals() and %r not in locals()"
        source = pattern % (name.id, name.id)
        co = self._compile(source)
        try:
            return self.frame.eval(co)
        except Exception:
            return False

    def visit_Attribute(self, attr):
        if not isinstance(attr.ctx, ast.Load):
            return self.generic_visit(attr)
        source_explanation, source_result = self.visit(attr.value)
        explanation = "%s.%s" % (source_explanation, attr.attr)
        source = "__exprinfo_expr.%s" % (attr.attr,)
        co = self._compile(source)
        try:
            result = self.frame.eval(co, __exprinfo_expr=source_result)
        except Exception:
            raise Failure(explanation)
        explanation = "%s\n{%s = %s.%s\n}" % \
                      (self.frame.repr(result), self.frame.repr(result), source_explanation, attr.attr)
        # Check if the attr is from an instance.
        source = "%r in getattr(__exprinfo_expr, '__dict__', {})"
        source = source % (attr.attr,)
        co = self._compile(source)
        try:
            from_instance = self.frame.eval(co, __exprinfo_expr=source_result)
        except Exception:
            from_instance = True
        if from_instance:
            rep = self.frame.repr(result)
            pattern = "%s\n{%s = %s\n}"
            explanation = pattern % (rep, rep, explanation)
        return explanation, result

    def visit_Assert(self, assrt):
        test_explanation, test_result = self.visit(assrt.test)
        if test_explanation.startswith("False\n{False =") and \
                test_explanation.endswith("\n"):
            test_explanation = test_explanation[15:-2]
        explanation = "assert %s" % (test_explanation,)
        if not test_result:
            try:
                raise builtins.AssertionError
            except Exception:
                raise Failure(explanation)
        return explanation, test_result

    def visit_Assign(self, assign):
        value_explanation, value_result = self.visit(assign.value)
        explanation = "... = %s" % (value_explanation,)
        name = ast.Name("__exprinfo_expr", ast.Load(),
                        lineno=assign.value.lineno,
                        col_offset=assign.value.col_offset)
        new_assign = ast.Assign(assign.targets, name, lineno=assign.lineno,
                                col_offset=assign.col_offset)
        mod = ast.Module([new_assign])
        co = self._compile(mod, "exec")
        try:
            self.frame.exec_(co, __exprinfo_expr=value_result)
        except Exception:
            raise Failure(explanation)
        return explanation, value_result
