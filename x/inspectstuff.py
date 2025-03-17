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
import inspect
import linecache
import re


##


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
            if node.decorator_list:
                line_number = node.decorator_list[0].lineno
            else:
                line_number = node.lineno

            # decrement by one since lines starts with indexing by zero
            line_number -= 1
            raise ClassFoundException(line_number)
        self.generic_visit(node)
        self.stack.pop()


def findsource(obj):
    """
    Return the entire source file and starting line number for an object.

    The argument may be a module, class, method, function, traceback, frame, or code object.  The source code is
    returned as a list of all the lines in the file and the line number indexes a line in that list.  An OSError is
    raised if the source code cannot be retrieved.
    """

    file = inspect.getsourcefile(obj)
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
    if module:
        lines = linecache.getlines(file, module.__dict__)
    else:
        lines = linecache.getlines(file)
    if not lines:
        raise OSError('could not get source code')

    if inspect.ismodule(obj):
        return lines, 0

    if inspect.isclass(obj):
        qualname = obj.__qualname__
        source = ''.join(lines)
        tree = ast.parse(source)
        class_finder = _ClassFinder(qualname)
        try:
            class_finder.visit(tree)
        except inspect.ClassFoundException as e:
            line_number = e.args[0]
            return lines, line_number
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
        pat = re.compile(r'^(\s*def\s)|(\s*async\s+def\s)|(.*(?<!\w)lambda(:|\s))|^(\s*@)')
        while lnum > 0:
            try:
                line = lines[lnum]
            except IndexError:
                raise OSError('lineno is out of bounds')
            if pat.match(line):
                break
            lnum = lnum - 1
        return lines, lnum

    raise OSError('could not find code object')
