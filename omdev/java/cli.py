"""
See:
 - https://github.com/jbangdev/jbang
 - https://docs.oracle.com/en/java/javase/17/docs/specs/man/java.html#using-source-file-mode-to-launch-single-file-source-code-programs
"""  # noqa
import shutil
import subprocess
import tempfile
import typing as ta

from omlish import check
from omlish.argparse import all as ap

from .. import magic


##


class Cli(ap.Cli):
    @ap.cmd(
        ap.arg('--cwd'),
        ap.arg('--java'),
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

        deps: list[str] = []

        for src_magic in src_magics:
            if src_magic.key == '@omlish-jdeps':
                for dep in check.isinstance(src_magic.prepared, ta.Sequence):  # noqa
                    deps.append(dep)  # noqa

            elif src_magic.key == '@omlish-llm-author':
                pass

            else:
                raise KeyError(src_magic.key)

        #

        if not deps:
            proc = subprocess.run(
                [
                    self.args.java or 'java',
                    src_file,
                    *self.args.args,
                ],
                cwd=self.args.cwd,
                check=False,
            )

            return proc.returncode

        #

        tmp_dir = tempfile.mkdtemp()
        try:
            # proc = subprocess.run(
            #     [
            #         self.args.java or 'java',
            #         src_file,
            #         *self.args.args,
            #     ],
            #     cwd=self.args.cwd,
            #     check=False,
            # )
            raise NotImplementedError

        finally:
            shutil.rmtree(tmp_dir)

        return proc.returncode  # type: ignore[unreachable]  # noqa


def _main() -> None:
    Cli().cli_run_and_exit()


if __name__ == '__main__':
    _main()
