"""
-I/Users/spinlock/src/wrmsr/omnibus/.venv/include
-I/Users/spinlock/.pyenv/versions/3.8.12/include/python3.8
-c omnibus/_ext/cc/os.cc
-o build/temp.macosx-12.0-arm64-3.8/omnibus/_ext/cc/os.o
-std=c++14
"""
import os.path
import glob
import shutil


def test_junk():
    here = os.path.join(os.path.dirname(__file__))
    if os.path.exists(bdir := os.path.join(here, 'build')):
        shutil.rmtree(bdir)
    for f in glob.glob(os.path.join(here, '*.so')):
        os.remove(f)

    import x.c._distutils as du
    import x.c._distutils.extension

    ##

    ext = du.extension.Extension(
        'junk',
        sources=[os.path.abspath(os.path.join(here, '../junk.cc'))],
        extra_compile_args=['-std=c++14'],
        undef_macros=['BARF'],
    )

    from ..build_ext import BuildExt
    cmd_obj = BuildExt(BuildExt.Options(
        inplace=True,
        debug=True,
    ))
    cmd_obj.build_extension(ext)

    # from . import junk  # type: ignore  # noqa
    import junk  # type: ignore  # noqa

    print(junk.abctok())
    assert junk.junk() == 422
