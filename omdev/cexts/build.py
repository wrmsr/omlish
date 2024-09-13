import dataclasses as dc
import os.path
import sys
import sysconfig
import typing as ta

from omlish import check
from omlish import lang

from . import _distutils as du


CPP_STD = 'c++20'


@dc.dataclass(frozen=True)
class BuildExt:
    full_name: str
    src_file: str

    inplace: bool = dc.field(default=True, kw_only=True)
    debug: bool = dc.field(default=True, kw_only=True)
    force: bool = dc.field(default=False, kw_only=True)

    dry_run: bool = dc.field(default=False, kw_only=True)
    verbose: bool = dc.field(default=False, kw_only=True)

    extra_src_files: lang.SequenceNotStr[str] | None = dc.field(default=None, kw_only=True)
    include_dirs: lang.SequenceNotStr[str] | None = dc.field(default=None, kw_only=True)
    compile_args: lang.SequenceNotStr[str] | None = dc.field(default=None, kw_only=True)
    link_args: lang.SequenceNotStr[str] | None = dc.field(default=None, kw_only=True)
    define_macros: ta.Sequence[tuple[str, str]] | None = dc.field(default=None, kw_only=True)
    undef_macros: lang.SequenceNotStr[str] | None = dc.field(default=None, kw_only=True)

    def __post_init__(self) -> None:
        check.not_isinstance(self.compile_args, str)
        check.not_isinstance(self.link_args, str)


def build_ext(ext: BuildExt) -> str:
    extra_link_args: list[str] = []
    if sys.platform == 'darwin':
        extra_link_args.append('-Wl,-no_fixup_chains')

    du_ext = du.Extension(
        ext.full_name,
        sources=[
            ext.src_file,
            *(ext.extra_src_files or []),
        ],
        include_dirs=[
            os.path.dirname(ext.src_file),
            *(ext.include_dirs or []),
        ],
        extra_compile_args=[
            *([f'-std={CPP_STD}'] if any(ext.src_file.endswith(sf) for sf in ('cc', 'cpp')) else []),
            *(ext.compile_args or []),
        ],
        extra_link_args=[
            *extra_link_args,
            *(ext.link_args or []),
        ],
        define_macros=(list(ext.define_macros) if ext.define_macros is not None else None),
        undef_macros=(list(ext.undef_macros) if ext.undef_macros is not None else None),
    )

    cmd_obj = du.BuildExt(du.BuildExt.Options(
        inplace=ext.inplace,
        debug=ext.debug,
        force=ext.force,

        dry_run=ext.dry_run,
        verbose=ext.verbose,
    ))
    cmd_obj.build_extension(du_ext)

    so_file = os.path.join(
        os.path.dirname(ext.src_file),
        ''.join([
            ext.full_name.rpartition('.')[2],
            '.',
            sysconfig.get_config_var('SOABI'),
            sysconfig.get_config_var('SHLIB_SUFFIX'),
        ]),
    )

    return so_file
