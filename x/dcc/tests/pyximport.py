import imp
import logging
import os
import sys
import traceback
import zipimport


log = logging.getLogger(__name__)


mod_name = "pyximport"

PYX_EXT = ".pyx"
PYXDEP_EXT = ".pyxdep"
PYXBLD_EXT = ".pyxbld"

DEBUG_IMPORT = False


def load_module(
        name,
        pyxfilename,
        pyxbuild_dir=None,
        is_package=False,
        build_inplace=False,
        language_level=None,
        so_path=None,
):
    try:
        if so_path is None:
            if is_package:
                module_name = name + '.__init__'
            else:
                module_name = name
                
            so_path = build_module(
                module_name,
                pyxfilename,
                pyxbuild_dir,
                inplace=build_inplace,
                language_level=language_level,
            )
            
        mod = imp.load_dynamic(name, so_path)
        if is_package and not hasattr(mod, '__path__'):
            mod.__path__ = [os.path.dirname(so_path)]
        assert mod.__file__ == so_path, (mod.__file__, so_path)
        
    except Exception:
        if pyxargs.load_py_module_on_import_failure and pyxfilename.endswith('.py'):
            # try to fall back to normal import
            mod = imp.load_source(name, pyxfilename)
            assert mod.__file__ in (pyxfilename, pyxfilename + 'c', pyxfilename + 'o'), (mod.__file__, pyxfilename)
            
        else:
            tb = sys.exc_info()[2]
            exc = ImportError("Building module %s failed: %s" % (name, traceback.format_exception_only(*sys.exc_info()[:2])))
            if sys.version_info[0] >= 3:
                raise exc.with_traceback(tb)
            else:
                exec("raise exc, None, tb", {'exc': exc, 'tb': tb})

    return mod


# import hooks

class PyxImporter:

    def __init__(
            self,
            extension=PYX_EXT,
            pyxbuild_dir=None,
            inplace=False,
            language_level=None,
    ):
        super().__init__()
        self.extension = extension
        self.pyxbuild_dir = pyxbuild_dir
        self.inplace = inplace
        self.language_level = language_level

    def find_module(self, fullname, package_path=None):
        if fullname in sys.modules and not pyxargs.reload_support:
            return None  # only here when reload()

        # package_path might be a _NamespacePath. Convert that into a list...
        if package_path is not None and not isinstance(package_path, list):
            package_path = list(package_path)

        try:
            fp, pathname, (ext, mode, ty) = imp.find_module(fullname, package_path)
            if fp:
                fp.close()  # Python should offer a Default-Loader to avoid this double find/open!

            if pathname and ty == imp.PKG_DIRECTORY:
                pkg_file = os.path.join(pathname, '__init__' + self.extension)
                if os.path.isfile(pkg_file):
                    return PyxLoader(
                        fullname,
                        pathname,
                        init_path=pkg_file,
                        pyxbuild_dir=self.pyxbuild_dir,
                        inplace=self.inplace,
                        language_level=self.language_level,
                    )
                
            if pathname and pathname.endswith(self.extension):
                return PyxLoader(
                    fullname,
                    pathname,
                    pyxbuild_dir=self.pyxbuild_dir,
                    inplace=self.inplace,
                    language_level=self.language_level,
                )

            if ty != imp.C_EXTENSION:  # only when an extension, check if we have a .pyx next!
                return None

            # find .pyx fast, when .so/.pyd exist --inplace
            pyxpath = os.path.splitext(pathname)[0] + self.extension
            if os.path.isfile(pyxpath):
                return PyxLoader(
                    fullname,
                    pyxpath,
                    pyxbuild_dir=self.pyxbuild_dir,
                    inplace=self.inplace,
                    language_level=self.language_level,
                )

            # .so/.pyd's on PATH should not be remote from .pyx's
            # think no need to implement PyxArgs.importer_search_remote here?

        except ImportError:
            pass

        # searching sys.path ...

        # if DEBUG_IMPORT:  print "SEARCHING", fullname, package_path

        mod_parts = fullname.split('.')
        module_name = mod_parts[-1]
        pyx_module_name = module_name + self.extension

        # this may work, but it returns the file content, not its path
        # import pkgutil
        # pyx_source = pkgutil.get_data(package, pyx_module_name)

        paths = package_path or sys.path
        for path in paths:
            pyx_data = None
            if not path:
                path = os.getcwd()
                
            elif os.path.isfile(path):
                try:
                    zi = zipimport.zipimporter(path)
                    pyx_data = zi.get_data(pyx_module_name)
                except (zipimport.ZipImportError, IOError, OSError):
                    continue  # Module not found.
                # unzip the imported file into the build dir
                # FIXME: can interfere with later imports if build dir is in sys.path and comes before zip file
                path = self.pyxbuild_dir
                
            elif not os.path.isabs(path):
                path = os.path.abspath(path)

            pyx_module_path = os.path.join(path, pyx_module_name)
            if pyx_data is not None:
                if not os.path.exists(path):
                    try:
                        os.makedirs(path)
                    except OSError:
                        # concurrency issue?
                        if not os.path.exists(path):
                            raise
                with open(pyx_module_path, "wb") as f:
                    f.write(pyx_data)

            elif not os.path.isfile(pyx_module_path):
                continue  # Module not found.

            return PyxLoader(
                fullname,
                pyx_module_path,
                pyxbuild_dir=self.pyxbuild_dir,
                inplace=self.inplace,
                language_level=self.language_level,
            )

        # not found, normal package, not a .pyx file, none of our business
        log.debug("%s not found" % fullname)
        return None


class PyImporter(PyxImporter):
    """A meta-path importer for normal .py files."""

    def __init__(self, pyxbuild_dir=None, inplace=False, language_level=None):
        if language_level is None:
            language_level = sys.version_info[0]
            
        super().__init__(
            extension='.py',
            pyxbuild_dir=pyxbuild_dir,
            inplace=inplace,
            language_level=language_level,
        )
        
        self.uncompilable_modules = {}
        
        self.blocked_modules = [
            'Cython',
            'pyxbuild',
            'pyximport.pyxbuild',
            'distutils.extension',
            'distutils.sysconfig',
        ]

    def find_module(self, fullname, package_path=None):
        if fullname in sys.modules:
            return None
        
        if fullname.startswith('Cython.'):
            return None
        
        if fullname in self.blocked_modules:
            # prevent infinite recursion
            return None
        
        if _lib_loader.knows(fullname):
            return _lib_loader
        
        log.debug("trying import of module '%s'", fullname)
        if fullname in self.uncompilable_modules:
            path, last_modified = self.uncompilable_modules[fullname]
            try:
                new_last_modified = os.stat(path).st_mtime
                if new_last_modified > last_modified:
                    # import would fail again
                    return None
            except OSError:
                # module is no longer where we found it, retry the import
                pass

        self.blocked_modules.append(fullname)
        try:
            importer = super().find_module(fullname, package_path)
            if importer is not None:
                if importer.init_path:
                    path = importer.init_path
                    real_name = fullname + '.__init__'
                else:
                    path = importer.path
                    real_name = fullname
                    
                log.debug("importer found path %s for module %s", path, real_name)
                try:
                    so_path = build_module(
                        real_name,
                        path,
                        pyxbuild_dir=self.pyxbuild_dir,
                        language_level=self.language_level,
                        inplace=self.inplace,
                    )
                    
                    _lib_loader.add_lib(
                        fullname,
                        path,
                        so_path,
                        is_package=bool(importer.init_path),
                    )
                    
                    return _lib_loader
                
                except Exception:
                    if DEBUG_IMPORT:
                        traceback.print_exc()
                    # build failed, not a compilable Python module
                    try:
                        last_modified = os.stat(path).st_mtime
                    except OSError:
                        last_modified = 0
                    self.uncompilable_modules[fullname] = (path, last_modified)
                    importer = None

        finally:
            self.blocked_modules.pop()
            
        return importer


class LibLoader:
    def __init__(self):
        super().__init__()
        self._libs = {}

    def load_module(self, fullname):
        try:
            source_path, so_path, is_package = self._libs[fullname]
        except KeyError:
            raise ValueError("invalid module %s" % fullname)
        log.debug("Loading shared library module '%s' from %s", fullname, so_path)
        return load_module(fullname, source_path, so_path=so_path, is_package=is_package)

    def add_lib(self, fullname, path, so_path, is_package):
        self._libs[fullname] = (path, so_path, is_package)

    def knows(self, fullname):
        return fullname in self._libs


_lib_loader = LibLoader()


class PyxLoader:
    def __init__(
            self,
            fullname,
            path,
            init_path=None,
            pyxbuild_dir=None,
            inplace=False,
            language_level=None,
    ):
        super().__init__()
        log.debug("PyxLoader created for loading %s from %s (init path: %s)", fullname, path, init_path)
        self.fullname = fullname
        self.path, self.init_path = path, init_path
        self.pyxbuild_dir = pyxbuild_dir
        self.inplace = inplace
        self.language_level = language_level

    def load_module(self, fullname):
        assert self.fullname == fullname, ("invalid module, expected %s, got %s" % (self.fullname, fullname))
        
        if self.init_path:
            # package
            # print "PACKAGE", fullname
            module = load_module(
                fullname,
                self.init_path,
                self.pyxbuild_dir,
                is_package=True,
                build_inplace=self.inplace,
                language_level=self.language_level,
            )
            module.__path__ = [self.path]
            
        else:
            # print "MODULE", fullname
            module = load_module(
                fullname,
                self.path,
                self.pyxbuild_dir,
                build_inplace=self.inplace,
                language_level=self.language_level,
            )
            
        return module


# install args
class PyxArgs:
    build_dir = True
    build_in_temp = True
    setup_args = {}  # None


##pyxargs=None


def _have_importers():
    has_py_importer = False
    has_pyx_importer = False
    for importer in sys.meta_path:
        if isinstance(importer, PyxImporter):
            if isinstance(importer, PyImporter):
                has_py_importer = True
            else:
                has_pyx_importer = True

    return has_py_importer, has_pyx_importer


def install(
        pyximport=True,
        pyimport=False,
        build_dir=None,
        build_in_temp=True,
        setup_args=None,
        reload_support=False,
        load_py_module_on_import_failure=False,
        inplace=False,
        language_level=None,
):
    """ Main entry point for pyxinstall.

    Call this to install the ``.pyx`` import hook in
    your meta-path for a single Python process.  If you want it to be
    installed whenever you use Python, add it to your ``sitecustomize``
    (as described above).

    :param pyximport: If set to False, does not try to import ``.pyx`` files.

    :param pyimport: You can pass ``pyimport=True`` to also
        install the ``.py`` import hook
        in your meta-path.  Note, however, that it is rather experimental,
        will not work at all for some ``.py`` files and packages, and will
        heavily slow down your imports due to search and compilation.
        Use at your own risk.

    :param build_dir: By default, compiled modules will end up in a ``.pyxbld``
        directory in the user's home directory.  Passing a different path
        as ``build_dir`` will override this.

    :param build_in_temp: If ``False``, will produce the C files locally. Working
        with complex dependencies and debugging becomes more easy. This
        can principally interfere with existing files of the same name.

    :param setup_args: Dict of arguments for Distribution.
        See ``distutils.core.setup()``.

    :param reload_support: Enables support for dynamic
        ``reload(my_module)``, e.g. after a change in the Cython code.
        Additional files ``<so_path>.reloadNN`` may arise on that account, when
        the previously loaded module file cannot be overwritten.

    :param load_py_module_on_import_failure: If the compilation of a ``.py``
        file succeeds, but the subsequent import fails for some reason,
        retry the import with the normal ``.py`` module instead of the
        compiled module.  Note that this may lead to unpredictable results
        for modules that change the system state during their import, as
        the second import will rerun these modifications in whatever state
        the system was left after the import of the compiled module
        failed.

    :param inplace: Install the compiled module
        (``.so`` for Linux and Mac / ``.pyd`` for Windows)
        next to the source file.

    :param language_level: The source language level to use: 2 or 3.
        The default is to use the language level of the current Python
        runtime for .py files and Py2 for ``.pyx`` files.
    """

    if setup_args is None:
        setup_args = {}
    if not build_dir:
        build_dir = os.path.join(os.path.expanduser('~'), '.pyxbld')

    global pyxargs
    pyxargs = PyxArgs()  # $pycheck_no
    pyxargs.build_dir = build_dir
    pyxargs.build_in_temp = build_in_temp
    pyxargs.setup_args = (setup_args or {}).copy()
    pyxargs.reload_support = reload_support
    pyxargs.load_py_module_on_import_failure = load_py_module_on_import_failure

    has_py_importer, has_pyx_importer = _have_importers()
    py_importer, pyx_importer = None, None

    if pyimport and not has_py_importer:
        py_importer = PyImporter(
            pyxbuild_dir=build_dir,
            inplace=inplace,
            language_level=language_level,
        )
        # make sure we import Cython before we install the import hook
        import Cython.Compiler.Main, Cython.Compiler.Pipeline, Cython.Compiler.Optimize
        sys.meta_path.insert(0, py_importer)

    if pyximport and not has_pyx_importer:
        pyx_importer = PyxImporter(
            pyxbuild_dir=build_dir,
            inplace=inplace,
            language_level=language_level,
        )
        sys.meta_path.append(pyx_importer)

    return py_importer, pyx_importer


def uninstall(py_importer, pyx_importer):
    try:
        sys.meta_path.remove(py_importer)
    except ValueError:
        pass

    try:
        sys.meta_path.remove(pyx_importer)
    except ValueError:
        pass
