"""
FIXME:
 - debug tables don't handle symlinks
 - use relapths in cml.txt

TODO:
 - symlink headers, included src files (hamt_impl, ...)
 - point / copy output to dst dirs
 - libs
  - ..
   - pybind
   - catch2?
   - json? https://github.com/nlohmann/json
  - FindPackages? FetchContent? built_ext won't have that
  - move omml git / data retriever stuff into omdev, get just the one header file from git via sha?
 - support local built pys 

==

Done:
 - https://intellij-support.jetbrains.com/hc/en-us/community/posts/206608485-Multiple-Jetbrain-IDE-sharing-the-same-project-directory really?
  - aight, generate a whole cmake subdir with symlinks to src files lol

"""  # noqa
import argparse
import dataclasses as dc
import io
import logging
import os.path
import shutil
import sys
import sysconfig
import typing as ta

from omlish import check
from omlish import lang
from omlish import logs

from .. import cmake
from .. import findmagic
from .magic import CextMagic


log = logging.getLogger(__name__)


##


def _sep_str_grps(*ls: ta.Sequence[str]) -> list[str]:
    o = []
    for i, l in enumerate(ls):
        if not l:
            continue
        if i:
            o.append('')
        o.extend(check.not_isinstance(l, str))
    return o


class CmakeProjectGen:
    def __init__(
            self,
            exts: ta.Sequence[str],
            prj_root: str | None = None,
            *,
            use_exe_realpath: bool = False,
    ) -> None:
        super().__init__()
        self._exts = check.not_isinstance(exts, str)
        self._prj_root = os.path.abspath(prj_root) if prj_root is not None else os.getcwd()
        self._use_exe_realpath = use_exe_realpath

    #

    @property
    def prj_root(self) -> str:
        return self._prj_root

    @lang.cached_function
    def prj_name(self) -> str:
        return os.path.basename(self.prj_root)

    @lang.cached_function
    def cmake_dir(self) -> str:
        cmake_dir = os.path.join(self.prj_root, 'cmake', self.prj_name())
        if os.path.exists(cmake_dir):
            for e in os.listdir(cmake_dir):
                if e == '.idea':
                    continue
                ep = os.path.join(cmake_dir, e)
                if os.path.isfile(ep):
                    os.unlink(ep)
                else:
                    shutil.rmtree(ep)
        else:
            os.makedirs(cmake_dir)
        return cmake_dir

    #

    def write_git_ignore(self) -> None:
        with open(os.path.join(self.cmake_dir(), '.gitignore'), 'w') as f:
            f.write('\n'.join(sorted(['/cmake-*', '/build'])))

    #

    @dc.dataclass(frozen=True, kw_only=True)
    class PyInfo:
        venv_exe: str
        venv_root: str
        real_exe: str
        root: str
        suffix: str

    @lang.cached_function
    def py_info(self) -> PyInfo:
        venv_exe = sys.executable
        real_exe = os.path.realpath(venv_exe)
        return self.PyInfo(
            venv_exe=venv_exe,
            venv_root=os.path.abspath(os.path.join(os.path.dirname(venv_exe), '..')),
            real_exe=real_exe,
            root=os.path.abspath(os.path.join(os.path.dirname(real_exe), '..')),
            suffix='.'.join(map(str, sys.version_info[:2])),
        )

    #

    @lang.cached_function
    def ext_files(self) -> ta.Sequence[str]:
        out = []
        for e in self._exts:
            e = os.path.abspath(e)
            if os.path.isfile(e):
                out.append(e)
            elif os.path.isdir(e):
                out.extend(
                    findmagic.find_magic(
                        [e],
                        [CextMagic.MAGIC_COMMENT],
                        CextMagic.FILE_EXTENSIONS,
                    ),
                )
            else:
                raise KeyError(e)
        return out

    #

    class _CmakeListsGen:
        def __init__(
                self,
                p: 'CmakeProjectGen',
                out: ta.TextIO,
        ) -> None:
            super().__init__()
            self.p = p
            self.g = cmake.CmakeGen(out)

        @lang.cached_property
        def var_prefix(self) -> str:
            return self.p.prj_name().upper()

        @lang.cached_property
        def py(self) -> 'CmakeProjectGen.PyInfo':
            return self.p.py_info()

        def _add_ext(self, ext_src: str) -> None:
            ext_name = ext_src.rpartition('.')[0].replace('/', '__')

            log.info('Adding cmake c extension: %s -> %s', ext_src, ext_name)

            so_name = ''.join([
                os.path.basename(ext_src).split('.')[0],
                '.',
                sysconfig.get_config_var('SOABI'),
                sysconfig.get_config_var('SHLIB_SUFFIX'),
            ])

            sl = os.path.join(self.p.cmake_dir(), ext_src)
            sal = os.path.abspath(sl)
            sd = os.path.dirname(sal)
            os.makedirs(sd, exist_ok=True)
            rp = os.path.relpath(os.path.abspath(ext_src), sd)
            os.symlink(rp, sal)

            ml = cmake.ModuleLibrary(
                ext_name,
                src_files=[
                    sl,
                ],
                include_dirs=[
                    f'${{{self.var_prefix}_INCLUDE_DIRECTORIES}}',
                ],
                compile_opts=[
                    f'${{{self.var_prefix}_COMPILE_OPTIONS}}',
                ],
                link_dirs=[
                    f'${{{self.var_prefix}_LINK_DIRECTORIES}}',
                ],
                link_libs=[
                    f'${{{self.var_prefix}_LINK_LIBRARIES}}',
                ],
                extra_cmds=[
                    cmake.Command(
                        'add_custom_command',
                        ['TARGET', ext_name, 'POST_BUILD'],
                        [
                            ' '.join([
                                'COMMAND ${CMAKE_COMMAND} -E ',
                                f'copy $<TARGET_FILE_NAME:{ext_name}> ../../../{os.path.dirname(ext_src)}/{so_name}',
                            ]),
                            'COMMAND_EXPAND_LISTS',
                        ],
                    ),
                ],
            )
            self.g.write_target(ml)

        def run(self) -> None:
            self.g.write(self.g.preamble)
            self.g.write('')

            self.g.write(f'project({self.p.prj_name()})')
            self.g.write('')

            self.g.write_var(cmake.Var(
                f'{self.var_prefix}_INCLUDE_DIRECTORIES',
                _sep_str_grps(
                    [f'{self.py.venv_root}/include'],
                    (
                        [
                            (red := os.path.dirname(self.p.py_info().real_exe)),
                            os.path.join(red, 'include'),
                        ]
                        if self.p._use_exe_realpath else  # noqa
                        [f'{self.py.root}/include/python{self.py.suffix}']
                    ),
                ),
            ))

            self.g.write_var(cmake.Var(
                f'{self.var_prefix}_COMPILE_OPTIONS',
                _sep_str_grps(
                    [
                        '-Wsign-compare',
                        '-Wunreachable-code',
                        '-DNDEBUG',
                        '-g',
                        '-fwrapv',
                        '-O3',
                        '-Wall',
                    ],
                    [
                        '-g',
                        '-c',
                    ],
                    ['-std=c++20'],
                ),
            ))

            self.g.write_var(cmake.Var(
                f'{self.var_prefix}_LINK_DIRECTORIES',
                _sep_str_grps(
                    (
                        [os.path.dirname(self.p.py_info().real_exe)]
                        if self.p._use_exe_realpath else  # noqa
                        [f'{self.py.root}/lib']
                    ),
                ),
            ))

            self.g.write_var(cmake.Var(
                f'{self.var_prefix}_LINK_LIBRARIES',
                _sep_str_grps(
                    *([[
                        '-bundle',
                        '"-undefined dynamic_lookup"',
                    ]] if sys.platform == 'darwin' else []),
                ),
            ))

            for ext_src in self.p.ext_files():
                self._add_ext(os.path.relpath(ext_src, self.p.prj_root))

    #

    def run(self) -> None:
        if not os.path.isfile(os.path.join(self._prj_root, 'pyproject.toml')):
            raise Exception('Must be run in project root')

        self.ext_files()

        log.info('Generating cmake project %s', self.prj_name())

        self.cmake_dir()
        self.write_git_ignore()

        out = io.StringIO()
        clg = self._CmakeListsGen(self, out)
        clg.run()

        with open(os.path.join(self.cmake_dir(), 'CMakeLists.txt'), 'w') as f:
            f.write(out.getvalue().strip() + '\n')


##


def _gen_cmd(args) -> None:
    if not args.exts:
        raise Exception('must specify exts')

    cpg = CmakeProjectGen(
        args.exts,
        use_exe_realpath=bool(args.realpath),
    )
    cpg.run()


def _main(argv=None) -> None:
    logs.configure_standard_logging('INFO')

    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers()

    parser_gen = subparsers.add_parser('gen')
    parser_gen.add_argument('--realpath', action='store_true')
    parser_gen.add_argument('exts', nargs='*')
    parser_gen.set_defaults(func=_gen_cmd)

    args = parser.parse_args(argv)
    if not getattr(args, 'func', None):
        parser.print_help()
    else:
        args.func(args)


if __name__ == '__main__':
    _main()
