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
import concurrent.futures as cf
import contextlib
import dataclasses as dc
import os
import re
import site
import sys
import typing as ta

import distutils as du
import distutils.core
import distutils.dep_util
import distutils.errors
import distutils.sysconfig
import distutils.util

from distutils import log

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

    def __init__(self, exts: ta.Iterable[du.core.Extension], opts: Options = Options()) -> None:
        super().__init__()

        self._exts = list(exts)
        self._opts = opts

        # build_py
        self.package_dir = {}

    # build_py

    package = None

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

    @property
    def options(self) -> Options:
        return self._opts

    @cached.property
    def build_base(self) -> str:
        return self._opts.build_base or 'build'

    @cached.property
    def plat_name(self) -> str:
        return self._opts.plat_name or du.util.get_platform()

    @cached.property
    def plat_specifier(self) -> str:
        ps = '.{}-{:d}.{:d}'.format(self.plat_name, *sys.version_info[:2])
        if hasattr(sys, 'gettotalrefcount'):
            ps += '-pydebug'
        return ps

    @cached.property
    def build_lib(self) -> str:
        return self._opts.build_lib or os.path.join(self.build_base, 'lib' + self.plat_specifier)

    @cached.property
    def build_temp(self) -> str:
        if self._opts.build_temp:
            return self._opts.build_temp
        bt = os.path.join(self.build_base, 'temp' + self.plat_specifier)
        if os.name == 'nt':
            if self._opts.debug:
                bt = os.path.join(bt, 'Debug')
            else:
                bt = os.path.join(bt, 'Release')
        return bt

    @dc.dataclass(frozen=True)
    class CDirs:
        include: ta.Sequence[str]
        library: ta.Sequence[str]
        runtime: ta.Sequence[str]

    @cached.property
    def cdirs(self) -> CDirs:
        include_dirs = list(self._opts.include_dirs or [])
        library_dirs = list(self._opts.library_dirs or [])
        rpath = list(self._opts.rpath or [])

        plat_py_include = du.sysconfig.get_python_inc(plat_specific=1)  # noqa

        if sys.exec_prefix != sys.base_exec_prefix:
            include_dirs.append(os.path.join(sys.exec_prefix, 'include'))

        py_include = du.sysconfig.get_python_inc()
        include_dirs.extend(py_include.split(os.path.pathsep))
        if plat_py_include != py_include:
            include_dirs.extend(plat_py_include.split(os.path.pathsep))

        if os.name == 'nt':
            library_dirs.append(os.path.join(sys.exec_prefix, 'libs'))
            if sys.base_exec_prefix != sys.prefix:  # Issue 16116
                library_dirs.append(os.path.join(sys.base_exec_prefix, 'libs'))

            include_dirs.append(os.path.dirname(du.sysconfig.get_config_h_filename()))
            _sys_home = getattr(sys, '_home', None)
            if _sys_home:
                library_dirs.append(_sys_home)

            if self.plat_name == 'win32':
                suffix = 'win32'
            else:
                suffix = self.plat_name[4:]
            new_lib = os.path.join(sys.exec_prefix, 'PCbuild')
            if suffix:
                new_lib = os.path.join(new_lib, suffix)
            library_dirs.append(new_lib)

        if sys.platform[:6] == 'cygwin':
            if sys.executable.startswith(os.path.join(sys.exec_prefix, 'bin')):
                library_dirs.append(os.path.join(sys.prefix, 'lib', 'python' + du.sysconfig.get_python_version(), 'config'))  # noqa
            else:
                library_dirs.append('.')

        if (du.sysconfig.get_config_var('Py_ENABLE_SHARED')):
            if not du.sysconfig.python_build:  # noqa
                library_dirs.append(du.sysconfig.get_config_var('LIBDIR'))
            else:
                # building python standard extensions
                library_dirs.append('.')

        if self._opts.user:
            user_include = os.path.join(site.USER_BASE, 'include')
            if os.path.isdir(user_include):
                include_dirs.append(user_include)

            user_lib = os.path.join(site.USER_BASE, 'lib')
            if os.path.isdir(user_lib):
                library_dirs.append(user_lib)
                rpath.append(user_lib)

        return BuildExt.CDirs(
            include=include_dirs,
            library=library_dirs,
            runtime=rpath,
        )

    def finalize_options(self):
        opts = self.Options()

        self.define = None
        if opts.define:
            self.define = [(symbol, '1') for symbol in opts.define]

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

        du.sysconfig.customize_compiler(self.compiler)
        if os.name == 'nt' and self.plat_name != du.util.get_platform():
            self.compiler.initialize(self.plat_name)  # noqa

        self.compiler.set_include_dirs(list(self.cdirs.include))
        if self.define is not None:
            # 'define' option is a list of (name,value) tuples
            for (name, value) in self.define:
                self.compiler.define_macro(name, value)
        if self._opts.undef is not None:
            for macro in self._opts.undef:
                self.compiler.undefine_macro(macro)
        if self._opts.libraries:
            self.compiler.set_libraries(list(self._opts.libraries))
        self.compiler.set_library_dirs(list(self.cdirs.library))
        self.compiler.set_runtime_library_dirs(list(self.cdirs.runtime))
        if self._opts.link_objects:
            self.compiler.set_link_objects(list(self._opts.link_objects))

        # Now actually compile and link everything.
        self.build_extensions()

    def get_source_files(self):
        filenames = []

        for ext in self._exts:
            filenames.extend(ext.sources)
        return filenames

    def get_outputs(self):
        outputs = []
        for ext in self._exts:
            outputs.append(self.get_ext_fullpath(ext.name))
        return outputs

    def build_extensions(self):
        if self._opts.parallel is not None:
            self._build_extensions_parallel()
        else:
            self._build_extensions_serial()

    def _build_extensions_parallel(self):
        workers = self._opts.parallel
        if workers < 1:
            workers = os.cpu_count()  # may return None

        if workers is None:
            self._build_extensions_serial()
            return

        with cf.ThreadPoolExecutor(max_workers=workers) as executor:
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
        except (du.errors.CCompilerError, du.errors.DistutilsError, du.errors.CompileError) as e:
            if not ext.optional:
                raise
            log.warn('building extension "%s" failed: %s' % (ext.name, e))

    def build_extension(self, ext):
        sources = ext.sources
        sources = sorted(sources)

        ext_path = self.get_ext_fullpath(ext.name)
        depends = sources + ext.depends
        if not (self._opts.force or du.dep_util.newer_group(depends, ext_path, 'newer')):
            log.debug('skipping "%s" extension (up-to-date)', ext.name)
            return
        else:
            log.info('building "%s" extension', ext.name)

        extra_args = ext.extra_compile_args or []

        macros = ext.define_macros[:]
        for undef in ext.undef_macros:
            macros.append((undef,))

        objects = self.compiler.compile(
            sources,
            output_dir=self.build_temp,
            macros=macros,
            include_dirs=ext.include_dirs,
            debug=int(self._opts.debug),  # noqa
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
        ext_path = ext_name.split('.')
        ext_suffix = du.sysconfig.get_config_var('EXT_SUFFIX')
        return os.path.join(*ext_path) + ext_suffix

    def get_export_symbols(self, ext):
        suffix = '_' + ext.name.split('.')[-1]
        try:
            # Unicode module name support as defined in PEP-489
            # https://www.python.org/dev/peps/pep-0489/#export-hook-name
            suffix.encode('ascii')
        except UnicodeEncodeError:
            suffix = 'U' + suffix.encode('punycode').replace(b'-', b'_').decode('ascii')

        initfunc_name = 'PyInit' + suffix
        if initfunc_name not in ext.export_symbols:
            ext.export_symbols.append(initfunc_name)
        return ext.export_symbols

    def get_libraries(self, ext):
        if sys.platform == 'win32':
            from distutils._msvccompiler import MSVCCompiler  # noqa
            if not isinstance(self.compiler, MSVCCompiler):
                template = 'python%d%d'
                if self._opts.debug:
                    template = template + '_d'
                pythonlib = (template % (sys.hexversion >> 24, (sys.hexversion >> 16) & 0xff))
                return ext.libraries + [pythonlib]
        else:
            link_libpython = False
            if du.sysconfig.get_config_var('Py_ENABLE_SHARED'):
                if hasattr(sys, 'getandroidapilevel'):
                    link_libpython = True
                elif sys.platform == 'cygwin':
                    link_libpython = True
                elif '_PYTHON_HOST_PLATFORM' in os.environ:
                    # We are cross-compiling for one of the relevant platforms
                    if du.sysconfig.get_config_var('ANDROID_API_LEVEL') != 0:
                        link_libpython = True
                    elif du.sysconfig.get_config_var('MACHDEP') == 'cygwin':
                        link_libpython = True

            if link_libpython:
                ldversion = du.sysconfig.get_config_var('LDVERSION')
                return ext.libraries + ['python' + ldversion]

        return ext.libraries
