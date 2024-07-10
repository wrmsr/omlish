import os.path
import sys
import sysconfig

from . import _distutils as du


def build_ext(
        fullname: str,
        src_path: str,
) -> str:
    extra_link_args = []
    if sys.platform == 'darwin':
        extra_link_args.append('-Wl,-no_fixup_chains')

    ext = du.Extension(
        fullname,
        sources=[src_path],
        extra_compile_args=['-std=c++14'],
        extra_link_args=extra_link_args,
        undef_macros=['BARF'],
    )

    cmd_obj = du.BuildExt(du.BuildExt.Options(
        inplace=True,
        debug=True,
    ))
    cmd_obj.build_extension(ext)

    so_path = os.path.join(
        os.path.dirname(src_path),
        ''.join([
            fullname.rpartition('.')[2],
            '.',
            sysconfig.get_config_var('SOABI'),
            sysconfig.get_config_var('SHLIB_SUFFIX'),
        ]),
    )

    return so_path
