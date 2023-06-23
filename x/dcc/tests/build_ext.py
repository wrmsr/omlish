"""
PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2
--------------------------------------------

1. This LICENSE AGREEMENT is between the Python Software Foundation ("PSF"), and the Individual or Organization
("Licensee") accessing and otherwise using this software ("Python") in source or binary form and its associated
documentation.

2. Subject to the terms and conditions of this License Agreement, PSF hereby grants Licensee a nonexclusive,
royalty-free, world-wide license to reproduce, analyze, test, perform and/or display publicly, prepare derivative works,
distribute, and otherwise use Python alone or in any derivative version, provided, however, that PSF's License Agreement
and PSF's notice of copyright, i.e., "Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011,
2012, 2013, 2014, 2015, 2016, 2017 Python Software Foundation; All Rights Reserved" are retained in Python alone or in
any derivative version prepared by Licensee.

3. In the event Licensee prepares a derivative work that is based on or incorporates Python or any part thereof, and
wants to make the derivative work available to others as provided herein, then Licensee hereby agrees to include in any
such work a brief summary of the changes made to Python.

4. PSF is making Python available to Licensee on an "AS IS" basis.  PSF MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS
OR IMPLIED.  BY WAY OF EXAMPLE, BUT NOT LIMITATION, PSF MAKES NO AND DISCLAIMS ANY REPRESENTATION OR WARRANTY OF
MERCHANTABILITY OR FITNESS FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF PYTHON WILL NOT INFRINGE ANY THIRD PARTY
RIGHTS.

5. PSF SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF PYTHON FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL
DAMAGES OR LOSS AS A RESULT OF MODIFYING, DISTRIBUTING, OR OTHERWISE USING PYTHON, OR ANY DERIVATIVE THEREOF, EVEN IF
ADVISED OF THE POSSIBILITY THEREOF.

6. This License Agreement will automatically terminate upon a material breach of its terms and conditions.

7. Nothing in this License Agreement shall be deemed to create any relationship of agency, partnership, or joint venture
between PSF and Licensee.  This License Agreement does not grant permission to use PSF trademarks or trade name in a
trademark sense to endorse or promote products or services of Licensee, or any third party.

8. By copying, installing or otherwise using Python, Licensee agrees to be bound by the terms and conditions of this
License Agreement.
"""
import contextlib
import os
import re
import sys
from distutils.errors import *
from distutils.sysconfig import customize_compiler, get_python_version
from distutils.sysconfig import get_config_h_filename
from distutils.dep_util import newer_group
from distutils.extension import Extension
from distutils.util import get_platform, convert_path
from distutils import log
import dataclasses as dc
import typing as ta

from site import USER_BASE

from omlish import check
from omlish import cached


extension_name_re = re.compile(r'^[a-zA-Z_][a-zA-Z_0-9]*(\.[a-zA-Z_][a-zA-Z_0-9]*)*$')


class BuildExt:

    @dc.dataclass(frozen=True)
    class Options:
        build_base: ta.Optional[str] = None
        build_lib: ta.Optional[str] = None  # directory for compiled extension modules
        build_temp: ta.Optional[str] = None  # directory for temporary files (build by-products)
        plat_name: ta.Optional[str] = None  # platform name to cross-compile for, if supported
        inplace: bool = False  # ignore build-lib and put compiled extensions into the source directory
        include_dirs: ta.Optional[ta.Sequence[str]] = None  # list of directories to search for header files (pathsep)
        define: ta.Optional[ta.Sequence[str]] = None  # C preprocessor macros to define
        undef: ta.Optional[ta.Sequence[str]] = None  # C preprocessor macros to undefine
        libraries: ta.Optional[ta.Sequence[str]] = None  # external C libraries to link with
        library_dirs: ta.Optional[ta.Sequence[str]] = None  # directories to search for external C libraries (pathsep)
        rpath: ta.Optional[ta.Sequence[str]] = None  # directories to search for shared C libraries at runtime
        link_objects: ta.Optional[ta.Sequence[str]] = None  # extra explicit link objects to include in the link
        debug: bool = False  # compile/link with debugging information
        force: bool = False  # forcibly build everything (ignore file timestamps)
        compiler: ta.Optional[str] = None  # specify the compiler type
        parallel: ta.Optional[int] = None  # number of parallel build jobs
        user: bool = False  # add user include, library and rpath

        dry_run: bool = False
        verbose: bool = False

    def __init__(self, exts: ta.Iterable[Extension], opts: Options = Options()) -> None:
        super().__init__()

        self._exts = list(exts)
        self._opts = opts

        # build_py
        self.package_dir = {}

    # build_py

    def get_package_dir(self, package):
        path = package.split('.')

        if not self.package_dir:
            if path:
                return os.path.join(*path)
            else:
                return ''
        else:
            tail = []
            while path:
                try:
                    pdir = self.package_dir['.'.join(path)]
                except KeyError:
                    tail.insert(0, path[-1])
                    del path[-1]
                else:
                    tail.insert(0, pdir)
                    return os.path.join(*tail)
            else:
                pdir = self.package_dir.get('')
                if pdir is not None:
                    tail.insert(0, pdir)

                if tail:
                    return os.path.join(*tail)
                else:
                    return ''

    # build_ext

    def finalize_options(self):
        opts = self.Options()

        self.build_base = opts.build_base or 'build'

        ##

        from distutils import sysconfig

        ## build

        self.plat_name = opts.plat_name
        if self.plat_name is None:
            self.plat_name = get_platform()
        else:
            if os.name != 'nt':
                raise DistutilsOptionError("--plat-name only supported on Windows (try " "using './configure --help' on your platform)")

        plat_specifier = ".%s-%d.%d" % (self.plat_name, *sys.version_info[:2])

        if hasattr(sys, 'gettotalrefcount'):
            plat_specifier += '-pydebug'

        self.build_lib = opts.build_lib
        if self.build_lib is None:
            self.build_lib = os.path.join(self.build_base, 'lib' + plat_specifier)

        self.build_temp = opts.build_temp
        if self.build_temp is None:
            self.build_temp = os.path.join(self.build_base, 'temp' + plat_specifier)

        ## build_ext

        self.package = None

        py_include = sysconfig.get_python_inc()
        plat_py_include = sysconfig.get_python_inc(plat_specific=1)
        self.include_dirs = list(opts.include_dirs or [])
        if isinstance(self.include_dirs, str):
            self.include_dirs = self.include_dirs.split(os.pathsep)

        if sys.exec_prefix != sys.base_exec_prefix:
            self.include_dirs.append(os.path.join(sys.exec_prefix, 'include'))

        self.include_dirs.extend(py_include.split(os.path.pathsep))
        if plat_py_include != py_include:
            self.include_dirs.extend(plat_py_include.split(os.path.pathsep))

        self.libraries = list(opts.libraries or [])
        self.link_objects = list(opts.link_objects or [])

        self.library_dirs = list(opts.library_dirs or [])
        if self.library_dirs is None:
            self.library_dirs = []
        elif isinstance(self.library_dirs, str):
            self.library_dirs = self.library_dirs.split(os.pathsep)

        self.rpath = list(opts.rpath or [])

        if os.name == 'nt':
            self.library_dirs.append(os.path.join(sys.exec_prefix, 'libs'))
            if sys.base_exec_prefix != sys.prefix:  # Issue 16116
                self.library_dirs.append(os.path.join(sys.base_exec_prefix, 'libs'))
            if self._opts.debug:
                self.build_temp = os.path.join(self.build_temp, "Debug")
            else:
                self.build_temp = os.path.join(self.build_temp, "Release")

            self.include_dirs.append(os.path.dirname(get_config_h_filename()))
            _sys_home = getattr(sys, '_home', None)
            if _sys_home:
                self.library_dirs.append(_sys_home)

            if self.plat_name == 'win32':
                suffix = 'win32'
            else:
                suffix = self.plat_name[4:]
            new_lib = os.path.join(sys.exec_prefix, 'PCbuild')
            if suffix:
                new_lib = os.path.join(new_lib, suffix)
            self.library_dirs.append(new_lib)

        if sys.platform[:6] == 'cygwin':
            if sys.executable.startswith(os.path.join(sys.exec_prefix, "bin")):
                self.library_dirs.append(os.path.join(sys.prefix, "lib", "python" + get_python_version(), "config"))
            else:
                self.library_dirs.append('.')

        if (sysconfig.get_config_var('Py_ENABLE_SHARED')):
            if not sysconfig.python_build:
                self.library_dirs.append(sysconfig.get_config_var('LIBDIR'))
            else:
                # building python standard extensions
                self.library_dirs.append('.')

        self.define = None
        if opts.define:
            self.define = [(symbol, '1') for symbol in opts.define]

        self.undef = opts.undef

        if self._opts.user:
            user_include = os.path.join(USER_BASE, "include")
            user_lib = os.path.join(USER_BASE, "lib")
            if os.path.isdir(user_include):
                self.include_dirs.append(user_include)
            if os.path.isdir(user_lib):
                self.library_dirs.append(user_lib)
                self.rpath.append(user_lib)

    def run(self):
        from distutils.ccompiler import new_compiler

        if not self._exts:
            return

        # FIXME: note build_clib
        # if self.distribution.has_c_libraries():
        #     build_clib = self.get_finalized_command('build_clib')
        #     self.libraries.extend(build_clib.get_library_names() or [])
        #     self.library_dirs.append(build_clib.build_clib)

        self.compiler = new_compiler(
            compiler=self._opts.compiler,
            verbose=int(self._opts.verbose),
            dry_run=int(self._opts.dry_run),
            force=int(self._opts.force),
        )

        customize_compiler(self.compiler)
        if os.name == 'nt' and self.plat_name != get_platform():
            self.compiler.initialize(self.plat_name)

        if self.include_dirs is not None:
            self.compiler.set_include_dirs(self.include_dirs)
        if self.define is not None:
            # 'define' option is a list of (name,value) tuples
            for (name, value) in self.define:
                self.compiler.define_macro(name, value)
        if self.undef is not None:
            for macro in self.undef:
                self.compiler.undefine_macro(macro)
        if self.libraries is not None:
            self.compiler.set_libraries(self.libraries)
        if self.library_dirs is not None:
            self.compiler.set_library_dirs(self.library_dirs)
        if self.rpath is not None:
            self.compiler.set_runtime_library_dirs(self.rpath)
        if self.link_objects is not None:
            self.compiler.set_link_objects(self.link_objects)

        # Now actually compile and link everything.
        self.build_extensions()

    def check_extensions_list(self, extensions):
        if not isinstance(extensions, list):
            raise DistutilsSetupError("'ext_modules' option must be a list of Extension instances")

        for i, ext in enumerate(extensions):
            if isinstance(ext, Extension):
                continue  # OK! (assume type-checking done
                # by Extension constructor)

            if not isinstance(ext, tuple) or len(ext) != 2:
                raise DistutilsSetupError(
                    "each element of 'ext_modules' option must be an " "Extension instance or 2-tuple")

            ext_name, build_info = ext

            log.warn(
                "old-style (ext_name, build_info) tuple found in " "ext_modules for extension '%s' " "-- please convert to Extension instance",
                ext_name)

            if not (isinstance(ext_name, str) and
                    extension_name_re.match(ext_name)):
                raise DistutilsSetupError(
                    "first element of each tuple in 'ext_modules' " "must be the extension name (a string)")

            if not isinstance(build_info, dict):
                raise DistutilsSetupError(
                    "second element of each tuple in 'ext_modules' " "must be a dictionary (build info)")

            # OK, the (ext_name, build_info) dict is type-safe: convert it
            # to an Extension instance.
            ext = Extension(ext_name, build_info['sources'])

            # Easy stuff: one-to-one mapping from dict elements to
            # instance attributes.
            for key in (
                    'include_dirs',
                    'library_dirs',
                    'libraries',
                    'extra_objects',
                    'extra_compile_args',
                    'extra_link_args',
            ):
                val = build_info.get(key)
                if val is not None:
                    setattr(ext, key, val)

            # Medium-easy stuff: same syntax/semantics, different names.
            ext.runtime_library_dirs = build_info.get('rpath')
            if 'def_file' in build_info:
                log.warn("'def_file' element of build info dict " "no longer supported")

            # Non-trivial stuff: 'macros' split into 'define_macros'
            # and 'undef_macros'.
            macros = build_info.get('macros')
            if macros:
                ext.define_macros = []
                ext.undef_macros = []
                for macro in macros:
                    if not (isinstance(macro, tuple) and len(macro) in (1, 2)):
                        raise DistutilsSetupError("'macros' element of build info dict " "must be 1- or 2-tuple")
                    if len(macro) == 1:
                        ext.undef_macros.append(macro[0])
                    elif len(macro) == 2:
                        ext.define_macros.append(macro)

            extensions[i] = ext

    def get_source_files(self):
        self.check_extensions_list(self._exts)
        filenames = []

        for ext in self._exts:
            filenames.extend(ext.sources)
        return filenames

    def get_outputs(self):
        self.check_extensions_list(self._exts)

        outputs = []
        for ext in self._exts:
            outputs.append(self.get_ext_fullpath(ext.name))
        return outputs

    def build_extensions(self):
        self.check_extensions_list(self._exts)
        if self._opts.parallel is not None:
            self._build_extensions_parallel()
        else:
            self._build_extensions_serial()

    def _build_extensions_parallel(self):
        workers = self._opts.parallel
        if workers < 1:
            workers = os.cpu_count()  # may return None
        from concurrent.futures import ThreadPoolExecutor

        if workers is None:
            self._build_extensions_serial()
            return

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(self.build_extension, ext) for ext in self._exts]
            for ext, fut in zip(self._exts, futures):
                with self._filter_build_errors(ext):
                    fut.result()

    def _build_extensions_serial(self):
        for ext in self._exts:
            with self._filter_build_errors(ext):
                self.build_extension(ext)

    @contextlib.contextmanager
    def _filter_build_errors(self, ext):
        try:
            yield
        except (CCompilerError, DistutilsError, CompileError) as e:
            if not ext.optional:
                raise
            self.warn('building extension "%s" failed: %s' %
                      (ext.name, e))

    def build_extension(self, ext):
        sources = ext.sources
        if sources is None or not isinstance(sources, (list, tuple)):
            raise DistutilsSetupError(
                "in 'ext_modules' option (extension '%s'), "
                "'sources' must be present and must be "
                "a list of source filenames" % ext.name)
        sources = sorted(sources)

        ext_path = self.get_ext_fullpath(ext.name)
        depends = sources + ext.depends
        if not (self._opts.force or newer_group(depends, ext_path, 'newer')):
            log.debug("skipping '%s' extension (up-to-date)", ext.name)
            return
        else:
            log.info("building '%s' extension", ext.name)

        extra_args = ext.extra_compile_args or []

        macros = ext.define_macros[:]
        for undef in ext.undef_macros:
            macros.append((undef,))

        objects = self.compiler.compile(
            sources,
            output_dir=self.build_temp,
            macros=macros,
            include_dirs=ext.include_dirs,
            debug=int(self._opts.debug),
            extra_postargs=extra_args,
            depends=ext.depends,
        )

        self._built_objects = objects[:]

        if ext.extra_objects:
            objects.extend(ext.extra_objects)
        extra_args = ext.extra_link_args or []

        language = ext.language or self.compiler.detect_language(sources)

        self.compiler.link_shared_object(
            objects, ext_path,
            libraries=self.get_libraries(ext),
            library_dirs=ext.library_dirs,
            runtime_library_dirs=ext.runtime_library_dirs,
            extra_postargs=extra_args,
            export_symbols=self.get_export_symbols(ext),
            debug=int(self._opts.debug),
            build_temp=self.build_temp,
            target_lang=language)

    def get_ext_fullpath(self, ext_name):
        fullname = self.get_ext_fullname(ext_name)
        modpath = fullname.split('.')
        filename = self.get_ext_filename(modpath[-1])

        if not self._opts.inplace:
            filename = os.path.join(*modpath[:-1] + [filename])
            return os.path.join(self.build_lib, filename)

        package = '.'.join(modpath[0:-1])
        package_dir = os.path.abspath(self.get_package_dir(package))

        return os.path.join(package_dir, filename)

    def get_ext_fullname(self, ext_name):
        if self.package is None:
            return ext_name
        else:
            return self.package + '.' + ext_name

    def get_ext_filename(self, ext_name):
        from distutils.sysconfig import get_config_var
        ext_path = ext_name.split('.')
        ext_suffix = get_config_var('EXT_SUFFIX')
        return os.path.join(*ext_path) + ext_suffix

    def get_export_symbols(self, ext):
        suffix = '_' + ext.name.split('.')[-1]
        try:
            # Unicode module name support as defined in PEP-489
            # https://www.python.org/dev/peps/pep-0489/#export-hook-name
            suffix.encode('ascii')
        except UnicodeEncodeError:
            suffix = 'U' + suffix.encode('punycode').replace(b'-', b'_').decode('ascii')

        initfunc_name = "PyInit" + suffix
        if initfunc_name not in ext.export_symbols:
            ext.export_symbols.append(initfunc_name)
        return ext.export_symbols

    def get_libraries(self, ext):
        if sys.platform == "win32":
            from distutils._msvccompiler import MSVCCompiler
            if not isinstance(self.compiler, MSVCCompiler):
                template = "python%d%d"
                if self._opts.debug:
                    template = template + '_d'
                pythonlib = (template % (sys.hexversion >> 24, (sys.hexversion >> 16) & 0xff))
                return ext.libraries + [pythonlib]
        else:
            from distutils.sysconfig import get_config_var
            link_libpython = False
            if get_config_var('Py_ENABLE_SHARED'):
                if hasattr(sys, 'getandroidapilevel'):
                    link_libpython = True
                elif sys.platform == 'cygwin':
                    link_libpython = True
                elif '_PYTHON_HOST_PLATFORM' in os.environ:
                    # We are cross-compiling for one of the relevant platforms
                    if get_config_var('ANDROID_API_LEVEL') != 0:
                        link_libpython = True
                    elif get_config_var('MACHDEP') == 'cygwin':
                        link_libpython = True

            if link_libpython:
                ldversion = get_config_var('LDVERSION')
                return ext.libraries + ['python' + ldversion]

        return ext.libraries
