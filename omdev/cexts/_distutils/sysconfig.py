"""
Provide access to Python's configuration information.  The specific configuration variables available depend heavily on
the platform and configuration.  The values may be retrieved using get_config_var(name), and the list of variables is
available via get_config_vars().keys().  Additional convenience functions are also available.

Written by:   Fred L. Drake, Jr.
Email:        <fdrake@acm.org>
"""
import functools
import os
import pathlib
import sys
import sysconfig

from .errors import DistutilsPlatformError
from .util import pass_none


IS_PYPY = '__pypy__' in sys.builtin_module_names

# These are needed in a couple of spots, so just compute them once.
PREFIX = os.path.normpath(sys.prefix)
EXEC_PREFIX = os.path.normpath(sys.exec_prefix)
BASE_PREFIX = os.path.normpath(sys.base_prefix)
BASE_EXEC_PREFIX = os.path.normpath(sys.base_exec_prefix)

# Path to the base directory of the project. On Windows the binary may live in project/PCbuild/win32 or
# project/PCbuild/amd64. set for cross builds
if '_PYTHON_PROJECT_BASE' in os.environ:
    project_base = os.path.abspath(os.environ['_PYTHON_PROJECT_BASE'])
elif sys.executable:
    project_base = os.path.dirname(os.path.abspath(sys.executable))
else:
    # sys.executable can be empty if argv[0] has been changed and Python is unable to retrieve the real program name
    project_base = os.getcwd()


def _is_python_source_dir(d):
    """Return True if the target directory appears to point to an un-installed Python."""
    modules = pathlib.Path(d).joinpath('Modules')
    return any(modules.joinpath(fn).is_file() for fn in ('Setup', 'Setup.local'))


_sys_home = getattr(sys, '_home', None)


def _is_parent(dir_a, dir_b):
    """Return True if a is a parent of b."""
    return os.path.normcase(dir_a).startswith(os.path.normcase(dir_b))


def _python_build():
    if _sys_home:
        return _is_python_source_dir(_sys_home)
    return _is_python_source_dir(project_base)


python_build = _python_build()

# Calculate the build qualifier flags if they are defined.  Adding the flags to the include and lib directories only
# makes sense for an installation, not an in-source build.
build_flags = ''
try:
    if not python_build:
        build_flags = sys.abiflags
except AttributeError:
    # It's not a configure-based build, so the sys module doesn't have this attribute, which is fine.
    pass


def get_python_version():
    """
    Return a string containing the major and minor Python version, leaving off the patchlevel.  Sample return values
    could be '1.5' or '2.2'.
    """
    return '%d.%d' % sys.version_info[:2]  # noqa


def get_python_inc(plat_specific=0, prefix=None):
    """
    Return the directory containing installed Python header files.

    If 'plat_specific' is false (the default), this is the path to the non-platform-specific header files, i.e.
    Python.h and so on; otherwise, this is the path to platform-specific header files (namely pyconfig.h).

    If 'prefix' is supplied, use it instead of sys.base_prefix or sys.base_exec_prefix -- i.e., ignore 'plat_specific'.
    """
    default_prefix = BASE_EXEC_PREFIX if plat_specific else BASE_PREFIX
    resolved_prefix = prefix if prefix is not None else default_prefix
    try:
        getter = globals()[f'_get_python_inc_{os.name}']
    except KeyError:
        raise DistutilsPlatformError("I don't know where Python installs its C header files on platform '%s'" % os.name) from None  # noqa
    return getter(resolved_prefix, prefix, plat_specific)


@pass_none
def _extant(path):
    """Replace path with None if it doesn't exist."""
    return path if os.path.exists(path) else None


def _get_python_inc_posix(prefix, spec_prefix, plat_specific):
    if IS_PYPY and sys.version_info < (3, 8):
        return os.path.join(prefix, 'include')
    return (
        _get_python_inc_posix_python(plat_specific)
        or _extant(_get_python_inc_from_config(plat_specific, spec_prefix))
        or _get_python_inc_posix_prefix(prefix)
    )


def _get_python_inc_posix_python(plat_specific):
    """
    Assume the executable is in the build directory. The pyconfig.h file should be in the same directory. Since the
    build directory may not be the source directory, use "srcdir" from the makefile to find the "Include" directory.
    """
    if not python_build:
        return None
    if plat_specific:
        return _sys_home or project_base
    incdir = os.path.join(get_config_var('srcdir'), 'Include')
    return os.path.normpath(incdir)


def _get_python_inc_from_config(plat_specific, spec_prefix):
    """
    If no prefix was explicitly specified, provide the include directory from the config vars. Useful when
    cross-compiling, since the config vars may come from the host platform Python installation, while the current Python
    executable is from the build platform installation.

    >>> monkeypatch = getfixture('monkeypatch')
    >>> gpifc = _get_python_inc_from_config
    >>> monkeypatch.setitem(gpifc.__globals__, 'get_config_var', str.lower)
    >>> gpifc(False, '/usr/bin/')
    >>> gpifc(False, '')
    >>> gpifc(False, None)
    'includepy'
    >>> gpifc(True, None)
    'confincludepy'
    """
    if spec_prefix is None:
        return get_config_var('CONF' * plat_specific + 'INCLUDEPY')
    return None


def _get_python_inc_posix_prefix(prefix):
    implementation = 'pypy' if IS_PYPY else 'python'
    python_dir = implementation + get_python_version() + build_flags
    return os.path.join(prefix, 'include', python_dir)


def _get_python_inc_nt(prefix, spec_prefix, plat_specific):
    if python_build:
        # Include both include dirs to ensure we can find pyconfig.h
        return (
            os.path.join(prefix, 'include') +
            os.path.pathsep +
            os.path.dirname(sysconfig.get_config_h_filename())
        )
    return os.path.join(prefix, 'include')


# allow this behavior to be monkey-patched. Ref pypa/distutils#2.
def _posix_lib(standard_lib, libpython, early_prefix, prefix):
    if standard_lib:
        return libpython
    else:
        return os.path.join(libpython, 'site-packages')


def get_python_lib(plat_specific=0, standard_lib=0, prefix=None):
    """
    Return the directory containing the Python library (standard or site additions).

    If 'plat_specific' is true, return the directory containing platform-specific modules, i.e. any module from a
    non-pure-Python module distribution; otherwise, return the platform-shared library directory.  If 'standard_lib' is
    true, return the directory containing standard Python library modules; otherwise, return the directory for
    site-specific modules.

    If 'prefix' is supplied, use it instead of sys.base_prefix or sys.base_exec_prefix -- i.e., ignore 'plat_specific'.
    """

    if IS_PYPY and sys.version_info < (3, 8):
        # PyPy-specific schema
        if prefix is None:
            prefix = PREFIX
        if standard_lib:
            return os.path.join(prefix, 'lib-python', str(sys.version_info[0]))
        return os.path.join(prefix, 'site-packages')

    early_prefix = prefix

    if prefix is None:
        if standard_lib:
            prefix = plat_specific and BASE_EXEC_PREFIX or BASE_PREFIX  # noqa
        else:
            prefix = plat_specific and EXEC_PREFIX or PREFIX  # noqa

    if os.name == 'posix':
        if plat_specific or standard_lib:
            # Platform-specific modules (any module from a non-pure-Python module distribution) or standard Python
            # library modules.
            libdir = getattr(sys, 'platlibdir', 'lib')
        else:
            # Pure Python
            libdir = 'lib'
        implementation = 'pypy' if IS_PYPY else 'python'
        libpython = os.path.join(prefix, libdir, implementation + get_python_version())
        return _posix_lib(standard_lib, libpython, early_prefix, prefix)
    else:
        raise DistutilsPlatformError(f"I don't know where Python installs its library on platform '{os.name}'")


@functools.lru_cache
def _customize_macos():
    """
    Perform first-time customization of compiler-related config vars on macOS. Use after a compiler is known to be
    needed. This customization exists primarily to support Pythons from binary installers. The kind and paths to build
    tools on the user system may vary significantly from the system that Python itself was built on.  Also the user OS
    version and build tools may not support the same set of CPU architectures for universal builds.
    """

    sys.platform == 'darwin' and __import__('_osx_support').customize_compiler(
        get_config_vars(),
    )


def customize_compiler(compiler):  # noqa: C901
    """Do any platform-specific customization of a CCompiler instance.

    Mainly needed on Unix, so we can plug in the information that varies across Unices and is stored in Python's
    Makefile.
    """
    if compiler.compiler_type == 'unix':
        _customize_macos()

        (
            cc,
            cxx,
            cflags,
            ccshared,
            ldshared,
            shlib_suffix,
            ar,
            ar_flags,
        ) = get_config_vars(
            'CC',
            'CXX',
            'CFLAGS',
            'CCSHARED',
            'LDSHARED',
            'SHLIB_SUFFIX',
            'AR',
            'ARFLAGS',
        )

        if 'CC' in os.environ:
            newcc = os.environ['CC']
            if 'LDSHARED' not in os.environ and ldshared.startswith(cc):
                # If CC is overridden, use that as the default
                #       command for LDSHARED as well
                ldshared = newcc + ldshared[len(cc):]
            cc = newcc
        if 'CXX' in os.environ:
            cxx = os.environ['CXX']
        if 'LDSHARED' in os.environ:
            ldshared = os.environ['LDSHARED']
        if 'CPP' in os.environ:
            cpp = os.environ['CPP']
        else:
            cpp = cc + ' -E'  # not always
        if 'LDFLAGS' in os.environ:
            ldshared = ldshared + ' ' + os.environ['LDFLAGS']
        if 'CFLAGS' in os.environ:
            cflags = cflags + ' ' + os.environ['CFLAGS']
            ldshared = ldshared + ' ' + os.environ['CFLAGS']
        if 'CPPFLAGS' in os.environ:
            cpp = cpp + ' ' + os.environ['CPPFLAGS']
            cflags = cflags + ' ' + os.environ['CPPFLAGS']
            ldshared = ldshared + ' ' + os.environ['CPPFLAGS']
        if 'AR' in os.environ:
            ar = os.environ['AR']
        if 'ARFLAGS' in os.environ:
            archiver = ar + ' ' + os.environ['ARFLAGS']
        else:
            archiver = ar + ' ' + ar_flags

        cc_cmd = cc + ' ' + cflags
        compiler.set_executables(
            preprocessor=cpp,
            compiler=cc_cmd,
            compiler_so=cc_cmd + ' ' + ccshared,
            compiler_cxx=cxx,
            linker_so=ldshared,
            linker_exe=cc,
            archiver=archiver,
        )

        if 'RANLIB' in os.environ and compiler.executables.get('ranlib', None):
            compiler.set_executables(ranlib=os.environ['RANLIB'])

        compiler.shared_lib_extension = shlib_suffix


def get_config_h_filename():
    """Return full pathname of installed pyconfig.h file."""
    return sysconfig.get_config_h_filename()


def parse_config_h(fp, g=None):
    """
    Parse a config.h-style file.

    A dictionary containing name/value pairs is returned.  If an optional dictionary is passed in as the second
    argument, it is used instead of a new dictionary.
    """
    return sysconfig.parse_config_h(fp, vars=g)


_config_vars = None


def get_config_vars(*args):
    """
    With no arguments, return a dictionary of all configuration variables relevant for the current platform.  Generally
    this includes everything needed to build extensions and install both pure modules and extensions.  On Unix, this
    means every variable defined in Python's installed Makefile; on Windows it's a much smaller set.

    With arguments, return a list of values that result from looking up each argument in the configuration variable
    dictionary.
    """
    global _config_vars
    if _config_vars is None:
        _config_vars = sysconfig.get_config_vars().copy()

    return [_config_vars.get(name) for name in args] if args else _config_vars


def get_config_var(name):
    """
    Return the value of a single variable using the dictionary returned by 'get_config_vars()'.  Equivalent to
    get_config_vars().get(name)
    """
    if name == 'SO':
        import warnings

        warnings.warn('SO is deprecated, use EXT_SUFFIX', DeprecationWarning, 2)
    return get_config_vars().get(name)
