"""
TODO:
 - ext scanning
 - __revision__
 - entry_points

https://setuptools.pypa.io/en/latest/references/keywords.html
https://packaging.python.org/en/latest/specifications/pyproject-toml

How to build a C extension in keeping with PEP 517, i.e. with pyproject.toml instead of setup.py?
https://stackoverflow.com/a/66479252

https://github.com/pypa/sampleproject/blob/db5806e0a3204034c51b1c00dde7d5eb3fa2532e/setup.py

https://pip.pypa.io/en/stable/cli/pip_install/#vcs-support
vcs+protocol://repo_url/#egg=pkg&subdirectory=pkg_dir
'git+https://github.com/wrmsr/omlish@master#subdirectory=.pip/omlish'
"""

"""
# https://setuptools.pypa.io/en/latest/userguide/ext_modules.html#extension-api-reference

name (str) –
    the full name of the extension, including any packages – ie. not a filename or pathname, but Python dotted name

sources (list[str]) –
    list of source filenames, relative to the distribution root (where the setup script lives), in Unix form
    (slash-separated) for portability. Source files may be C, C++, SWIG (.i), platform-specific resource files, or
    whatever else is recognized by the “build_ext” command as source for a Python extension.

include_dirs (list[str]) –
    list of directories to search for C/C++ header files (in Unix form for portability)

define_macros (list[tuple[str, str|None]]) –
    list of macros to define; each macro is defined using a 2-tuple: the first item corresponding to the name of the
    macro and the second item either a string with its value or None to define it without a particular value (equivalent
    of “#define FOO” in source or -DFOO on Unix C compiler command line)

undef_macros (list[str]) –
    list of macros to undefine explicitly

library_dirs (list[str]) –
    list of directories to search for C/C++ libraries at link time

libraries (list[str]) –
    list of library names (not filenames or paths) to link against

runtime_library_dirs (list[str]) –
    list of directories to search for C/C++ libraries at run time (for shared extensions, this is when the extension is
    loaded). Setting this will cause an exception during build on Windows platforms.

extra_objects (list[str]) –
    list of extra files to link with (eg. object files not implied by ‘sources’, static library that must be explicitly
    specified, binary resource files, etc.)

extra_compile_args (list[str]) –
    any extra platform- and compiler-specific information to use when compiling the source files in ‘sources’. For
    platforms and compilers where “command line” makes sense, this is typically a list of command-line arguments, but
    for other platforms it could be anything.

extra_link_args (list[str]) –
    any extra platform- and compiler-specific information to use when linking object files together to create the
    extension (or to create a new static Python interpreter). Similar interpretation as for ‘extra_compile_args’.

export_symbols (list[str]) –
    list of symbols to be exported from a shared extension. Not used on all platforms, and not generally necessary for
    Python extensions, which typically export exactly one symbol: “init” + extension_name.

swig_opts (list[str]) –
    any extra options to pass to SWIG if a source file has the .i extension.

depends (list[str]) –
    list of files that the extension depends on

language (str) –
    extension language (i.e. “c”, “c++”, “objc”). Will be detected from the source extensions if not provided.

optional (bool) –
    specifies that a build failure in the extension should not abort the build process, but simply not install the
    failing extension.

py_limited_api (bool) –
    opt-in flag for the usage of Python’s limited API.
"""
import dataclasses as dc
import importlib
import os.path
import shutil
import subprocess
import sys
import typing as ta

from omdev.toml.writer import TomlWriter


##


SETUP_PY_TMPL = """
import setuptools as st

st.setup(
    ext_modules=[
        st.Extension(
            'mypackage.mymodule',
            [
                'lib/mymodule.c',
                'lib/mypackage.c',
                'lib/myalloc.c',
            ],
            include_dirs=['lib'],
            py_limited_api=True
        ),
    ],
)
"""


@dc.dataclass(frozen=True)
class Ext:
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


##


def build_cls_dct(cls: type) -> ta.Dict[str, ta.Any]:
    dct = {}
    for b in reversed(cls.__mro__):
        for k, v in b.__dict__.items():
            if k.startswith('_'):
                continue
            dct[k] = v
    return dct


def move_dict_key(sd: dict[str, ta.Any], sk: str, dd: dict[str, ta.Any], dk: str) -> None:
    if sk in sd:
        dd[dk] = sd.pop(sk)


def build_pypdist_dir(
        dir_name: str,
        project_cls: type,
        setuptools_cls: type,
        build_root: str,
        *,
        run_build: bool = False,
        build_output_dir: ta.Optional[str] = None,
) -> str:
    build_dir: str = os.path.join(build_root, dir_name)
    if os.path.isdir(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir)

    #

    os.symlink(os.path.relpath(dir_name, build_dir), os.path.join(build_dir, dir_name))

    #

    pyp_dct = {}

    #

    pyp_dct['build-system'] = {
        'requires': ['setuptools'],
        'build-backend': 'setuptools.build_meta',
    }

    prj = build_cls_dct(project_cls)
    pyp_dct['project'] = prj
    move_dict_key(prj, 'optional_dependencies', pyp_dct, 'project.optional-dependencies')

    st = build_cls_dct(setuptools_cls)
    pyp_dct['tool.setuptools'] = st
    move_dict_key(st, 'find_packages', pyp_dct, 'tool.setuptools.packages.find')

    mani_in = st.pop('manifest_in', None)

    with open(os.path.join(build_dir, 'pyproject.toml'), 'w') as f:
        TomlWriter(f).write_root(pyp_dct)

    #

    if mani_in:
        with open(os.path.join(build_dir, 'MANIFEST.in'), 'w') as f:
            f.write('\n'.join(mani_in))  # noqa

    #

    for fn in [
        'LICENSE',
        'README.rst',
    ]:
        if os.path.exists(fn):
            os.symlink(os.path.relpath(fn, build_dir), os.path.join(build_dir, fn))

    #

    if run_build:
        subprocess.check_call(
            [
                sys.executable,
                '-m',
                'build',
            ],
            cwd=build_dir,
        )

        if build_output_dir is not None:
            dist_dir = os.path.join(build_dir, 'dist')
            for fn in os.listdir(dist_dir):
                shutil.copyfile(os.path.join(dist_dir, fn), os.path.join(build_output_dir, fn))

    #

    return build_dir


##


def _main() -> None:
    if not os.path.isfile('pyproject.toml'):
        raise RuntimeError('must run in project root')

    build_root = os.path.join('.pip')
    build_output_dir = 'dist'
    run_build = False

    if run_build:
        os.makedirs(build_output_dir, exist_ok=True)

    for dir_name in [
        'omlish',
        'omdev',
    ]:
        about = importlib.import_module(f'{dir_name}.__about__')
        build_pypdist_dir(
            dir_name,
            about.Project,
            about.Setuptools,
            build_root,
            run_build=run_build,
            build_output_dir=build_output_dir,
        )


if __name__ == '__main__':
    _main()
