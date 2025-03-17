# PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2
# --------------------------------------------
#
# 1. This LICENSE AGREEMENT is between the Python Software Foundation ("PSF"), and the Individual or Organization
# ("Licensee") accessing and otherwise using this software ("Python") in source or binary form and its associated
# documentation.
#
# 2. Subject to the terms and conditions of this License Agreement, PSF hereby grants Licensee a nonexclusive,
# royalty-free, world-wide license to reproduce, analyze, test, perform and/or display publicly, prepare derivative
# works, distribute, and otherwise use Python alone or in any derivative version, provided, however, that PSF's License
# Agreement and PSF's notice of copyright, i.e., "Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009,
# 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017 Python Software Foundation; All Rights Reserved" are retained in Python
# alone or in any derivative version prepared by Licensee.
#
# 3. In the event Licensee prepares a derivative work that is based on or incorporates Python or any part thereof, and
# wants to make the derivative work available to others as provided herein, then Licensee hereby agrees to include in
# any such work a brief summary of the changes made to Python.
#
# 4. PSF is making Python available to Licensee on an "AS IS" basis.  PSF MAKES NO REPRESENTATIONS OR WARRANTIES,
# EXPRESS OR IMPLIED.  BY WAY OF EXAMPLE, BUT NOT LIMITATION, PSF MAKES NO AND DISCLAIMS ANY REPRESENTATION OR WARRANTY
# OF MERCHANTABILITY OR FITNESS FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF PYTHON WILL NOT INFRINGE ANY THIRD PARTY
# RIGHTS.
#
# 5. PSF SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF PYTHON FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL
# DAMAGES OR LOSS AS A RESULT OF MODIFYING, DISTRIBUTING, OR OTHERWISE USING PYTHON, OR ANY DERIVATIVE THEREOF, EVEN IF
# ADVISED OF THE POSSIBILITY THEREOF.
#
# 6. This License Agreement will automatically terminate upon a material breach of its terms and conditions.
#
# 7. Nothing in this License Agreement shall be deemed to create any relationship of agency, partnership, or joint
# venture between PSF and Licensee.  This License Agreement does not grant permission to use PSF trademarks or trade
# name in a trademark sense to endorse or promote products or services of Licensee, or any third party.
#
# 8. By copying, installing or otherwise using Python, Licensee agrees to be bound by the terms and conditions of this
# License Agreement.
# https://github.com/python/cpython/blob/a936af924efc6e2fb59e27990dcd905b7819470a/Lib/inspect.py
import ast
import dataclasses as dc
import inspect
import linecache
import re
import types
import typing as ta


##


@dc.dataclass(frozen=True, kw_only=True)
class FoundSource:
    obj: ta.Any
    file: str
    module: types.ModuleType
    file_lines: ta.Sequence[str]
    line: int
    column: int | None = None
    end_line: int | None = None
    end_column: int | None = None


#


class _ClassFoundException(Exception):
    pass


class _ClassFinder(ast.NodeVisitor):
    def __init__(self, qualname):
        self.stack = []
        self.qualname = qualname

    def visit_FunctionDef(self, node):
        self.stack.append(node.name)
        self.stack.append('<locals>')
        self.generic_visit(node)
        self.stack.pop()
        self.stack.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node):
        self.stack.append(node.name)

        if self.qualname == '.'.join(self.stack):
            # Return the decorator for the class if present
            start_node = node
            if node.decorator_list:
                start_node = node.decorator_list[0]

            # decrement line numbers by one since lines starts with indexing by zero
            raise _ClassFoundException(dict(
                line=start_node.lineno - 1,
                column=start_node.col_offset,
                end_line=node.end_lineno - 1,
                end_column=node.end_col_offset,
            ))

        self.generic_visit(node)
        self.stack.pop()


#


_FIND_SOURCE_CODE_PAT = re.compile(
    r'^(\s*(?P<def>def)\s)|'
    r'(\s*(?P<async>async)\s+def\s)|'
    r'(.*(?<!\w)(?P<lambda>lambda)(:|\s))|'
    r'^(\s*(?P<decorator>@))'
)


def findsource(obj: ta.Any) -> FoundSource:
    """
    Return the entire source file and starting line number for an object.

    The argument may be a module, class, method, function, traceback, frame, or code object.  The source code is
    returned as a list of all the lines in the file and the line number indexes a line in that list.  An OSError is
    raised if the source code cannot be retrieved.
    """

    ret_kw: dict = dict(
        obj=obj,
    )

    file = inspect.getsourcefile(obj)
    ret_kw.update(file=file)
    if file:
        # Invalidate cache if needed.
        linecache.checkcache(file)
    else:
        file = inspect.getfile(obj)
        # Allow filenames in form of "<something>" to pass through. `doctest` monkeypatches `linecache` module to enable
        # inspection, so let `linecache.getlines` to be called.
        if not (file.startswith('<') and file.endswith('>')):
            raise OSError('source code not available')

    module = inspect.getmodule(obj, file)
    ret_kw.update(module=module)
    if module:
        lines = linecache.getlines(file, module.__dict__)
    else:
        lines = linecache.getlines(file)
    if not lines:
        raise OSError('could not get source code')
    ret_kw.update(file_lines=lines)

    if inspect.ismodule(obj):
        ret_kw.update(line=0)
        return FoundSource(**ret_kw)

    if inspect.isclass(obj):
        qualname = obj.__qualname__
        source = ''.join(lines)
        tree = ast.parse(source)
        class_finder = _ClassFinder(qualname)
        try:
            class_finder.visit(tree)
        except _ClassFoundException as e:
            ret_kw.update(**e.args[0])
            return FoundSource(**ret_kw)
        else:
            raise OSError('could not find class definition')

    if inspect.ismethod(obj):
        obj = obj.__func__
    if inspect.isfunction(obj):
        obj = obj.__code__
    if inspect.istraceback(obj):
        obj = obj.tb_frame
    if inspect.isframe(obj):
        obj = obj.f_code
    if inspect.iscode(obj):
        if not hasattr(obj, 'co_firstlineno'):
            raise OSError('could not find function definition')
        lnum = obj.co_firstlineno - 1
        while lnum > 0:
            try:
                line = lines[lnum]
            except IndexError:
                raise OSError('lineno is out of bounds')
            if (m := _FIND_SOURCE_CODE_PAT.match(line)) is not None:
                [span] = [m.span(g) for g, gv in m.groupdict().items() if gv is not None]
                ret_kw.update(column=span[0])
                break
            lnum = lnum - 1
        ret_kw.update(line=lnum)
        return FoundSource(**ret_kw)

    raise OSError('could not find code object')


class Foo:
    def bar(self):
        pass


def _main() -> None:
    print(findsource(Foo.bar))


if __name__ == '__main__':
    _main()
