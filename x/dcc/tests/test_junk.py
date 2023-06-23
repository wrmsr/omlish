"""
-I/Users/spinlock/src/wrmsr/omnibus/.venv/include
-I/Users/spinlock/.pyenv/versions/3.8.12/include/python3.8
-c omnibus/_ext/cc/os.cc
-o build/temp.macosx-12.0-arm64-3.8/omnibus/_ext/cc/os.o
-std=c++14
"""
import os.path
import sys


def test_junk():
    import distutils as du
    import distutils.ccompiler
    import distutils.core
    import distutils.sysconfig
    import distutils.util

    ##

    ext = du.core.Extension(
        'junk',
        sources=[os.path.abspath(os.path.join(os.path.dirname(__file__), '../junk.cc'))],
        extra_compile_args=['-std=c++14'],
    )

    from .build_ext import build_ext
    cmd_obj = build_ext()
    cmd_obj.extensions = [ext]
    cmd_obj.inplace = 1
    cmd_obj.ensure_finalized()
    cmd_obj.run()

    # ##
    #
    # cc = du.ccompiler.new_compiler()
    # distutils.sysconfig.customize_compiler(cc)
    #
    # ##
    #
    # plat_name = du.util.get_platform()
    # plat_specifier = ".{}-{:d}.{:d}".format(plat_name, *sys.version_info[:2])
    #
    # if hasattr(sys, 'gettotalrefcount'):
    #     plat_specifier += '-pydebug'
    #
    # build_base = 'build'
    # build_temp = os.path.join(build_base, 'temp' + plat_specifier)
    #
    # ##
    #
    # include_dirs = []
    #
    # # Make sure Python's include directories (for Python.h, pyconfig.h, etc.) are in the include search path.
    # py_include = du.sysconfig.get_python_inc()
    # plat_py_include = du.sysconfig.get_python_inc(plat_specific=1)  # noqa
    #
    # # If in a virtualenv, add its include directory. Issue 16116
    # if sys.exec_prefix != sys.base_exec_prefix:
    #     include_dirs.append(os.path.join(sys.exec_prefix, 'include'))
    #
    # # Put the Python "system" include dir at the end, so that any local include dirs take precedence.
    # include_dirs.extend(py_include.split(os.path.pathsep))
    # if plat_py_include != py_include:
    #     include_dirs.extend(plat_py_include.split(os.path.pathsep))
    #
    # ##
    #
    # debug = 0
    #
    # objects = cc.compile(
    #     ext.sources,
    #     output_dir=build_temp,
    #     debug=debug,  # noqa
    #     include_dirs=ext.include_dirs + include_dirs,
    #     extra_postargs=ext.extra_compile_args,
    # )
    #
    # print(objects)
    #
    # # Detect target language, if not provided
    # language = ext.language or cc.detect_language(ext.sources)
    #
    # ext_path = 'junk.so'
    #
    # cc.link_shared_object(
    #     objects,
    #     ext_path,
    #     libraries=self.get_libraries(ext),
    #     runtime_library_dirs=ext.runtime_library_dirs,
    #     extra_postargs=ext.extra_link_args,
    #     export_symbols=self.get_export_symbols(ext),
    #     debug=debug,  # noqa
    #     build_temp=build_temp,
    #     target_lang=language,
    # )
