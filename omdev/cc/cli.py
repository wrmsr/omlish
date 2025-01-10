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
 - gen cmake
"""
import dataclasses as dc
import os
import shlex
import shutil
import subprocess
import tempfile
import tomllib
import typing as ta

from omlish import cached
from omlish import check
from omlish import lang
from omlish import marshal as msh
from omlish.argparse import all as ap
from omlish.formats import json

from .. import magic
from ..cache import data as dcache


@dc.dataclass(frozen=True)
class Cdep:
    @dc.dataclass(frozen=True)
    class Git:
        url: str
        rev: str

        subtrees: ta.Sequence[str] | None = None

    git: Git

    include: ta.Sequence[str] | None = None


@cached.function
def load_cdeps() -> ta.Mapping[str, Cdep]:
    src = lang.get_relative_resources(globals=globals())['cdeps.toml'].read_text()
    dct = tomllib.loads(src)
    return msh.unmarshal(dct.get('deps', {}), ta.Mapping[str, Cdep])  # type: ignore


class Cli(ap.Cli):
    @ap.cmd(
        ap.arg('--cwd'),
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
                        dep = msh.unmarshal(dep, Cdep)  # type: ignore
                    else:
                        dep = load_cdeps()[check.isinstance(dep, str)]

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

            else:
                raise KeyError(src_magic.key)

        #

        src_file_name = os.path.basename(src_file)

        sh_parts: list[str] = [
            'clang++',
        ]

        for inc_dir in include_dirs:
            sh_parts.append(f'-I{shlex.quote(inc_dir)}')

        if cflags := os.environ.get('CFLAGS'):
            sh_parts.append(cflags)  # Explicitly shell-unquoted

        sh_parts.extend([
            '-std=c++20',
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


def _main() -> None:
    Cli().cli_run_and_exit()


if __name__ == '__main__':
    _main()
