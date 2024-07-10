"""
Provides exceptions used by the Distutils modules.  Note that Distutils modules may raise standard exceptions; in
particular, SystemExit is usually raised for errors that are obviously the end-user's fault (eg. bad command-line
arguments).

This module is safe to use in "from ... import *" mode; it only exports symbols whose names start with "Distutils" and
end with "Error".
"""


class DistutilsError(Exception):
    """The root of all Distutils evil."""


class DistutilsModuleError(DistutilsError):
    """
    Unable to load an expected module, or to find an expected class within some module (in particular, command modules
    and classes).
    """


class DistutilsFileError(DistutilsError):
    """
    Any problems in the filesystem: expected file not found, etc. Typically this is for problems that we detect before
    OSError could be raised.
    """


class DistutilsPlatformError(DistutilsError):
    """
    We don't know how to do something on the current platform (but we do know how to do it on some platform) -- eg.
    trying to compile C files on a platform not supported by a CCompiler subclass.
    """


class DistutilsExecError(DistutilsError):
    """Any problems executing an external program (such as the C compiler, when compiling C files)."""


class DistutilsInternalError(DistutilsError):
    """Internal inconsistencies or impossibilities (obviously, this should never be seen if the code is working!)."""


# Exception classes used by the CCompiler implementation classes
class CCompilerError(Exception):
    """Some compile/link operation failed."""


class CompileError(CCompilerError):
    """Failure to compile one or more C/C++ source files."""


class LibError(CCompilerError):
    """Failure to create a static library from one or more C/C++ object files."""


class LinkError(CCompilerError):
    """Failure to link one or more C/C++ object files into an executable or shared library file."""


class UnknownFileError(CCompilerError):
    """Attempt to process an unknown file type."""
