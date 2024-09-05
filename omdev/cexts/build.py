import os.path
import sys
import sysconfig

from . import _distutils as du


def build_ext(
        fullname: str,
        src_path: str,
) -> str:
    extra_link_args: list[str] = []
    if sys.platform == 'darwin':
        extra_link_args.append('-Wl,-no_fixup_chains')

    ext = du.Extension(
        fullname,
        sources=[src_path],
        include_dirs=[os.path.dirname(src_path)],
        extra_compile_args=[
            *(['-std=c++20'] if any(src_path.endswith(sf) for sf in ('cc', 'cpp')) else []),
        ],
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
