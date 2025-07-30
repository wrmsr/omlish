"""
//$(which true); exec om cc run "$0" "$@"
or
//usr/bin/true; exec om cc run "$0" "$@"

See: https://gist.github.com/jdarpinian/1952a58b823222627cc1a8b83a7aa4e2

==

Freestanding options:

//usr/bin/env clang++ -std=c++20 -o ${X=`mktemp`} "$0" && exec -a "$0" "$X" "$@"
//usr/bin/env clang++ -std=c++20 -o ${D=`mktemp -d`}/x "$0" && ${D}/x ${@:1}; R=$?; rm -rf ${D}; exit $R
//$(which true); clang++ -std=c++20 -o ${D=`mktemp -d`}/x ${0} && ${D}/x ${@:1}; R=${?}; rm -rf ${D}; exit ${R}

==

TODO:
 - cext interop
 - cc cmake
  - shlex shebang to extract opts
  - nanobind
  - 2 dep mechanisms? not necessarily bad
 - cc ij, based off of cmake
 - fix CFLAGS/CCFLAGS/CPPFLAGS/CXXFLAGS
 - jit-gen cmake mode? multi-src builds
"""
import os
import shlex
import shutil
import subprocess
import tempfile
import textwrap
import typing as ta

from omlish import check
from omlish import marshal as msh
from omlish.argparse import all as ap
from omlish.formats import json

from .. import intellij as ij
from .. import magic
from ..cache import data as dcache
from .cdeps import Cdep
from .cdeps import load_cdeps
from .cdeps import process_marshaled_cdep
from .srclangs import SRC_LANGS_BY_EXT
from .srclangs import SrcLangs


##


class Cli(ap.Cli):
    @ap.cmd(
        ap.arg('--cwd'),
        ap.arg('--cmd'),
        ap.arg('src-file'),
        ap.arg('args', nargs=ap.REMAINDER),
    )
    def run(self) -> int:
        src_file = self.args.src_file

        #

        with open(src_file) as f:
            src = f.read()

        src_magics = magic.find_magic(  # noqa
            magic.C_MAGIC_STYLE,
            src.splitlines(),
            file=src_file,
            preparer=magic.json_magic_preparer,
        )

        include_dirs: list[str] = []

        for src_magic in src_magics:
            if src_magic.key == '@omlish-cdeps':
                for dep in check.isinstance(src_magic.prepared, ta.Sequence):
                    if isinstance(dep, ta.Mapping):
                        dep = process_marshaled_cdep(dep)
                        dep = msh.unmarshal(dep, Cdep)
                    else:
                        dep = load_cdeps()[check.isinstance(dep, str)]

                    if dep.sources:
                        # TODO
                        raise NotImplementedError

                    dep_spec = dcache.GitSpec(
                        url=dep.git.url,
                        rev=dep.git.rev,
                        subtrees=dep.git.subtrees,
                    )
                    dep_dir = dcache.default().get(dep_spec)

                    for dep_inc in dep.include or []:
                        inc_dir = os.path.join(dep_dir, dep_inc)
                        check.state(os.path.isdir(inc_dir))
                        include_dirs.append(inc_dir)

            elif src_magic.key == '@omlish-llm-author':
                pass

            elif src_magic.key == '@omlish-cext':
                # FIXME: lol - usecase for non-cext bins?
                pass

            else:
                raise KeyError(src_magic.key)

        #

        src_file_name = os.path.basename(src_file)

        sl = SrcLangs.CPP
        if '.' in src_file:
            ext = src_file.rpartition('.')[2]
            sl = SRC_LANGS_BY_EXT.get(ext, sl)

        #

        sh_parts: list[str] = [
            self.args.cmd or sl.cmd,
        ]

        for inc_dir in include_dirs:
            sh_parts.append(f'-I{shlex.quote(inc_dir)}')

        if cflags := os.environ.get('CFLAGS'):
            sh_parts.append(cflags)  # Explicitly shell-unquoted

        if ldflags := os.environ.get('LDFLAGS'):
            sh_parts.append(ldflags)  # Explicitly shell-unquoted

        if sl.std is not None:
            sh_parts.append(f'-std={sl.std}')

        sh_parts.extend([
            shlex.quote(os.path.abspath(src_file)),
            '-o',
            shlex.quote(src_file_name),
        ])

        #

        tmp_dir = tempfile.mkdtemp()
        try:
            proc = subprocess.run(  # noqa
                ' '.join(sh_parts),
                cwd=tmp_dir,
                shell=True,
                check=False,
            )

            if rc := proc.returncode:
                return rc

            exe_file = os.path.join(tmp_dir, src_file_name)
            check.state(os.path.isfile(exe_file))

            proc = subprocess.run(
                [
                    exe_file,
                    *self.args.args,
                ],
                cwd=self.args.cwd,
                check=False,
            )

        finally:
            shutil.rmtree(tmp_dir)

        return proc.returncode

    # @ap.cmd(
    #     ap.arg('src-file', nargs='+'),
    # )
    # def add_shebang(self) -> None:
    #     # //$(which true); exec om cc run "$0" "$@"
    #     print(self.args.src_file)

    #

    @ap.cmd()
    def list_deps(self) -> None:
        cdeps = load_cdeps()
        print(json.dumps_pretty(msh.marshal(cdeps)))

    @ap.cmd(
        ap.arg('src-file'),
    )
    def ij(self) -> None:
        src_file = self.args.src_file
        src_file_name = os.path.basename(src_file)
        prj_name = src_file_name.rpartition('.')[0]

        # with open(src_file) as f:
        #     src = f.read()
        # shebang = src.splitlines()[0]
        # shebang_parts = shlex.split(shebang)
        # cc_run_pos = next(i for i in range(len(shebang_parts) - 1) if shebang_parts[i:i + 2] == ['cc', 'run'])
        # cc_run_args = shebang_parts[cc_run_pos + 2:]
        # print(cc_run_args)

        tmp_dir = tempfile.mkdtemp(f'__{prj_name}')

        src_dir = os.path.join(tmp_dir, 'src')
        os.mkdir(src_dir)

        os.symlink(os.path.abspath(src_file), os.path.join(src_dir, src_file_name))

        cmake_lists_src = textwrap.dedent(f"""\
            cmake_minimum_required(VERSION 3.14)
            project({prj_name})

            add_executable({prj_name} src/{src_file_name})

            set_target_properties({prj_name} PROPERTIES
                CXX_STANDARD 20
                CXX_STANDARD_REQUIRED YES
                CXX_EXTENSIONS NO
            )
        """)

        cmake_lists_path = os.path.join(tmp_dir, 'CMakeLists.txt')
        with open(cmake_lists_path, 'w') as f:
            f.write(cmake_lists_src)

        ij.open_ide(tmp_dir, ide=ij.Ide.CLION)


def _main() -> None:
    Cli().cli_run_and_exit()


if __name__ == '__main__':
    _main()
