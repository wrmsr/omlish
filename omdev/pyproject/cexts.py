# ruff: noqa: UP006 UP007
import dataclasses as dc
import typing as ta


"""
# https://setuptools.pypa.io/en/latest/userguide/ext_modules.html#extension-api-reference

name (str) -
    the full name of the extension, including any packages - ie. not a filename or pathname, but Python dotted name

sources (list[str]) -
    list of source filenames, relative to the distribution root (where the setup script lives), in Unix form
    (slash-separated) for portability. Source files may be C, C++, SWIG (.i), platform-specific resource files, or
    whatever else is recognized by the “build_ext” command as source for a Python extension.

include_dirs (list[str]) -
    list of directories to search for C/C++ header files (in Unix form for portability)

define_macros (list[tuple[str, str|None]]) -
    list of macros to define; each macro is defined using a 2-tuple: the first item corresponding to the name of the
    macro and the second item either a string with its value or None to define it without a particular value (equivalent
    of “#define FOO” in source or -DFOO on Unix C compiler command line)

undef_macros (list[str]) -
    list of macros to undefine explicitly

library_dirs (list[str]) -
    list of directories to search for C/C++ libraries at link time

libraries (list[str]) -
    list of library names (not filenames or paths) to link against

runtime_library_dirs (list[str]) -
    list of directories to search for C/C++ libraries at run time (for shared extensions, this is when the extension is
    loaded). Setting this will cause an exception during build on Windows platforms.

extra_objects (list[str]) -
    list of extra files to link with (eg. object files not implied by 'sources', static library that must be explicitly
    specified, binary resource files, etc.)

extra_compile_args (list[str]) -
    any extra platform- and compiler-specific information to use when compiling the source files in 'sources'. For
    platforms and compilers where “command line” makes sense, this is typically a list of command-line arguments, but
    for other platforms it could be anything.

extra_link_args (list[str]) -
    any extra platform- and compiler-specific information to use when linking object files together to create the
    extension (or to create a new static Python interpreter). Similar interpretation as for 'extra_compile_args'.

export_symbols (list[str]) -
    list of symbols to be exported from a shared extension. Not used on all platforms, and not generally necessary for
    Python extensions, which typically export exactly one symbol: “init” + extension_name.

swig_opts (list[str]) -
    any extra options to pass to SWIG if a source file has the .i extension.

depends (list[str]) -
    list of files that the extension depends on

language (str) -
    extension language (i.e. “c”, “c++”, “objc”). Will be detected from the source extensions if not provided.

optional (bool) -
    specifies that a build failure in the extension should not abort the build process, but simply not install the
    failing extension.

py_limited_api (bool) -
    opt-in flag for the usage of Python's limited API.
"""


SETUP_PY_TMPL = """
import setuptools as st

st.setup(
    ext_modules=[
        st.Extension(
            '{mod_name}',
            [{mod_srcs}],
            include_dirs=['lib'],
            py_limited_api=True
        ),
    ],
)
"""


@dc.dataclass(frozen=True)
class ExtModule:
    name: str
    sources: ta.List[str]
    include_dirs: ta.Optional[ta.List[str]] = None
    define_macros: ta.Optional[ta.List[ta.Tuple[str, ta.Optional[str]]]] = None
    undef_macros: ta.Optional[ta.List[str]] = None
    library_dirs: ta.Optional[ta.List[str]] = None
    libraries: ta.Optional[ta.List[str]] = None
    runtime_library_dirs: ta.Optional[ta.List[str]] = None
    extra_objects: ta.Optional[ta.List[str]] = None
    extra_compile_args: ta.Optional[ta.List[str]] = None
    extra_link_args: ta.Optional[ta.List[str]] = None
    export_symbols: ta.Optional[ta.List[str]] = None
    swig_opts: ta.Optional[ta.List[str]] = None
    depends: ta.Optional[ta.List[str]] = None
    language: ta.Optional[str] = None
    optional: ta.Optional[bool] = None
    py_limited_api: ta.Optional[bool] = None
