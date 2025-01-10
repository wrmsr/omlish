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
"""
import os
import shlex
import shutil
import subprocess
import tempfile

from omlish import check
from omlish.argparse import all as ap

from .. import magic
from ..cli import CliModule


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

        src_magic = magic.find_magic(  # noqa
            magic.C_MAGIC_STYLE,
            src.splitlines(),
            file=src_file,
            preparer=magic.json_magic_preparer,
        )

        # print(src_magic)

        #

        src_file_name = os.path.basename(src_file)

        sh_parts: list[str] = [
            'clang++',
        ]

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


def _main() -> None:
    Cli().cli_run_and_exit()


# @omlish-manifest
_CLI_MODULE = CliModule('cc', __name__)


if __name__ == '__main__':
    _main()
